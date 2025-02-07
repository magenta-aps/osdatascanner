import gzip
import json
import structlog
import pika
import time
import signal
import threading
import traceback
from sortedcontainers import SortedList

from ...utilities.backoff import ExponentialBackoffRetrier
from ....utils.system_utilities import json_utf8_decode
from os2datascanner.utils import pika_settings


logger = structlog.get_logger("pika")


def go_bang(k):
    exc_type, exc_value, exc_traceback, thread = k
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    signal.raise_signal(signal.SIGKILL)


HandleMessageType = tuple[str, str, str, str] | tuple[str, str]

# We register an exception hook to make sure the main thread does not hang
# indefinitely should a problem arise in the rabbitmq-connection-thread.
threading.excepthook = go_bang


class PikaConnectionHolder:
    """A PikaConnectionHolder manages a blocking connection to a RabbitMQ
    server. (Like Pika itself, it is not thread safe.)"""

    def __init__(self, backoff=pika_settings.AMQP_BACKOFF_PARAMS, **kwargs):
        connection_params = {
            "host": pika_settings.AMQP_HOST,
            "port": pika_settings.AMQP_PORT,
            "virtual_host": pika_settings.AMQP_VHOST,
            "heartbeat": pika_settings.AMQP_HEARTBEAT,
        }
        connection_params.update(kwargs)
        credentials = pika.PlainCredentials(
            pika_settings.AMQP_USER, pika_settings.AMQP_PWD
        )
        self._parameters = pika.ConnectionParameters(
            credentials=credentials, **connection_params
        )
        self._connection = None
        self._channel = None
        self._backoff = backoff

    def make_connection(self):
        """Constructs a new Pika connection."""
        return pika.BlockingConnection(self._parameters)

    @property
    def connection(self):
        """Returns the managed Pika connection, creating one if necessary."""
        if not self.has_connection:
            self._connection = ExponentialBackoffRetrier(
                    pika.exceptions.AMQPConnectionError,
                    **self._backoff).run(self.make_connection)
        return self._connection

    @property
    def has_connection(self):
        return bool(self._connection)

    def make_channel(self):
        """Constructs a new Pika channel."""
        return self.connection.channel()

    @property
    def channel(self):
        """Returns the managed Pika channel, creating one (and a backing
        connection) if necessary."""
        if not self.has_channel:
            self._channel = self.make_channel()
        return self._channel

    @property
    def has_channel(self):
        return bool(self._channel)

    def clear(self):
        """Closes the managed Pika connection, if there is one."""
        try:
            if self.has_channel:
                self._channel.close()
        except pika.exceptions.ChannelWrongStateError:
            pass
        finally:
            self._channel = None

        try:
            if self.has_connection:
                self._connection.close()
        except pika.exceptions.ConnectionWrongStateError:
            pass
        finally:
            self._connection = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_info, exc_tb):
        self.clear()


ANON_QUEUE = ""
"""The special value that indicates to RabbitMQ that the broker should assign
a randomly-generated unique name to a queue. (When used to identify a queue to
read from, this value refers to the last randomly-generated queue name for the
given channel.)"""


class PikaPipelineRunner(PikaConnectionHolder):
    def __init__(self, *,
                 prefetch_count=1, read=None, write=None, **kwargs):
        super().__init__(**kwargs)
        self._read = set() if read is None else set(read)
        self._write = set() if write is None else set(write)
        self._prefetch_count = prefetch_count

    def make_channel(self):
        """As PikaConnectionHolder.make_channel, but automatically declares all
        of the read and write queues used by this pipeline stage.

        This method also declares a durable fanout exchange called "broadcast"
        used by some OSdatascanner components to send and receive global
        messages."""
        channel = super().make_channel()
        channel.basic_qos(prefetch_count=self._prefetch_count)
        for q in self._read.union(self._write):
            channel.queue_declare(
                    q,
                    passive=False,
                    durable=True,
                    exclusive=False,
                    auto_delete=False)

        channel.exchange_declare(
            "broadcast", pika.spec.ExchangeType.fanout,
            passive=False, durable=True, auto_delete=False, internal=False)

        return channel

    def handle_message_raw(self, channel, method, properties, body):
        """Handles an AMQP message.

        The default implementation of this method acknowledges the message and
        otherwise does nothing."""
        self.channel.basic_ack(method.delivery_tag)

    def _basic_consume(self, *, exclusive=False):
        """Registers this PikaPipelineRunner to receive messages directed to
        its read queues. (Be sure to call _basic_cancel with the return value
        of this function to cancel this registration later.)

        Subclasses can override this function to subscribe to additional
        queues, but should usually begin by calling the superclass
        implementation."""
        consumer_tags = {}
        for queue in self._read:
            consumer_tags[queue] = (self.channel.basic_consume(
                    queue, self.handle_message_raw,
                    exclusive=exclusive))
        return consumer_tags

    def _basic_cancel(self, consumer_tags: dict):
        """Cancels all of the provided consumer registrations."""
        for tag in consumer_tags.values():
            self.channel.basic_cancel(tag)


class RejectMessage(BaseException):
    """Implementations of PikaPipelineThread.handle_message can raise the
    RejectMessage exception to indicate that a message should be rejected. (By
    default, messages are acknowledged once handle_message is finished.)

    Rejected messages are by default re-enqueued for later execution; if
    requeue=False is passed to the constructor, though, messages will just be
    dropped.

    This exception is not intended to be handled by anything other than
    PikaPipelineThread, and is accordingly implemented as a BaseException
    rather than an Exception."""

    def __init__(self, *args, requeue=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.requeue = requeue


_coders = {
    "gzip": (gzip.compress, gzip.decompress)
}


class SynchronisationTimeoutError(RuntimeError):
    """When the PikaPipelineThread.synchronise method fails due to a timeout,
    the SynchronisationTimeoutError exception is raised."""


class PikaPipelineThread(threading.Thread, PikaPipelineRunner):
    """Runs a Pika session in a background thread."""

    def __init__(self, *args, exclusive=False, **kwargs):
        super().__init__()
        PikaPipelineRunner.__init__(self, *args, **kwargs)

        self._incoming = SortedList(key=lambda e: -(e[1].priority or 0))
        self._outgoing = []
        self._live = None
        self._condition = threading.Condition()
        self._exclusive = exclusive
        self._default_basic_properties = dict(delivery_mode=2, content_encoding="gzip")
        self._tick = 0

        self._shutdown_exception = None

    def _enqueue(self, label: str, *args, check_live=True):
        """Enqueues a request for the background thread, optionally checking
        whether or not it's already finished.

        Requests consist of a label that specifies the desired action and a
        number of action-specific parameters. This is an implementation detail:
        clients should use the enqueue_* methods instead."""
        with self._condition:
            if check_live and self.ident is not None and not self.is_alive():
                raise RuntimeError(
                        "attempted to enqueue a request on a completed"
                        " PikaPipelineThread")
            logger.trace(f"PikaPipelineThread - Thread TID: {self.native_id} "
                         "acquired conditional and enqueued outgoing message.")
            self._outgoing.append((label, *args))

    def enqueue_ack(self, delivery_tag: int):
        """Requests that the background thread acknowledge receipt of the
        message with the given tag."""
        return self._enqueue("ack", delivery_tag)

    def enqueue_reject(self, delivery_tag: int, requeue: bool = True):
        """Requests that the background thread reject the message with the
        given tag."""
        return self._enqueue("rej", delivery_tag, requeue)

    def enqueue_stop(self):
        """Requests that the background thread stop running. (This is the only
        request that can be enqueued without producing an error if the
        background thread has already stopped.)

        Note that the background thread is *not* a daemon thread: the host
        process will not terminate if this method is never called."""
        return self._enqueue("fin", check_live=False)

    def enqueue_message(self,
                        routing_key: str,
                        body: bytes,
                        exchange: str = "",
                        **basic_properties):
        """Requests that the background thread send a message.

        Note that the content_encoding property gets special treatment: if it's
        set, the message will be encoded accordingly -- on the calling thread,
        not the background one -- before it's enqueued."""
        basic_properties = self._default_basic_properties | basic_properties

        if not isinstance(body, bytes):
            body = json.dumps(body).encode()
        if (encoding := basic_properties.get("content_encoding")):
            encoder, _ = _coders[encoding]
            body = encoder(body)

        return self._enqueue(
                "msg", routing_key, body, exchange, basic_properties)

    def _enqueue_pause(self, duration: float = 5.0):
        """Requests that the background thread wait for the specified duration.
        (This is chiefly useful for testing.)"""
        return self._enqueue("zzz", duration)

    def synchronise(self, timeout=None):
        """Blocks the current thread after requesting a wakeup from the
        background thread. The underlying communication mechanism is a
        threading.Event (although, unlike that class, a RuntimeError will be
        raised in the event of the given timeout elapsing).

        As requests sent to the background thread are executed in the order in
        which they were made, this function can be used to establish that the
        background thread has reached a certain point in the request queue.

        It is usually a bad idea to call this function without starting the
        background thread first, unless there's a third thread around to do
        that."""
        ev = threading.Event()
        self._enqueue("syn", ev)
        # I *think* spurious wakeups on events are impossible, as there's only
        # a simple flag and all waiters are released once it's set
        if ev.wait(timeout) is not True and timeout is not None:
            raise SynchronisationTimeoutError(
                    "PikaPipelineThread.synchronise timed out"
                    f" after {timeout} seconds")

    def await_message(self, timeout: float = None):
        """Returns a message collected by the background thread; the return
        value is the (method, properties, body) 3-tuple normally returned by
        BlockingConnection.basic_get. This method will return immediately if
        the background thread isn't running; otherwise, it will block until a
        message is available or until the given timeout elapses.

        Note that messages with a declared content encoding will be decoded
        automatically before being returned."""
        method, properties, body = None, None, None
        with self._condition:

            def waiter():
                return not self._live or len(self._incoming) > 0
            logger.trace(f"PikaPipelineThread - Thread TID: {self.native_id}"
                         " awaiting message: releasing lock and going to sleep...")
            rv = self._condition.wait_for(waiter, timeout)
            if rv and self._live:
                method, properties, body = self._incoming.pop(0)
        if body and properties and properties.content_encoding:
            _, decoder = _coders[properties.content_encoding]
            body = decoder(body)
            # We've decoded the content, so from this point on it should be
            # regarded as unencoded
            properties.content_encoding = None

        logger.trace(f"PikaPipelineThread - Thread TID: {self.native_id}"
                     " done sleeping. Got a message.")
        return method, properties, body

    def handle_message(self, routing_key, body) -> HandleMessageType:
        """Handles an AMQP message by yielding zero or more (routing key,
        JSON-serialisable object) pairs to be sent as new messages.

        The default implementation of this method does nothing."""
        yield from []

    def after_message(self, routing_key, body):
        """Performs an action of some kind after the given message has been
        processed and an acknowledgement has been enqueued. (Note that this
        function will not be called when a message is rejected.)

        The default implementation of this method does nothing."""

    def handle_message_raw(self, channel, method, properties, body):
        """(Background thread.) Collects a message and stores it for later
        retrieval by the main thread."""
        with self._condition:
            self._incoming.add((method, properties, body,))
            logger.trace(f"PikaPipelineThread - Thread TID: {self.native_id}"
                         " handled incoming message. Notifying other threads.")
            self._condition.notify()

    def _processing_complete(self, tick: int):
        """(Background thread.) General-purpose hook function called by run()
        every time it finishes processing the list of enqueued actions.

        The default implementation dispatches RabbitMQ heartbeat messages and
        calls handle_message_raw() for new channel messages before sleeping for
        a tenth of a second. Subclasses can override this method, but must
        eventually call up to the superclass implementation.

        The tick value passed to this method increases by one for every call
        made to it. Subclasses can check this value to gate routine operations
        that nonetheless don't need to be called ten times a second."""
        # Dispatch any waiting timer (heartbeats) and channel (calls to our
        # handle_message_raw method) callbacks...
        self.connection.process_data_events(0)
        # ... and then sleep for a moment to avoid overburdening the system
        time.sleep(0.1)

    def run(self):  # noqa: CCR001, too high cognitive complexity
        """(Background thread.) Runs a loop that processes enqueued actions
        from, and collects new messages for, the main thread.

        (Note that it *is* possible, if you're careful, to call this function
        directly in order to execute a list of enqueued actions on the current
        thread.)"""
        with self._condition:
            self._live = True
            self._condition.notify()
        consumer_tags = self._basic_consume(exclusive=self._exclusive)
        try:
            running = True
            while running:
                with self._condition:
                    # Process all of the enqueued actions
                    while self._outgoing:
                        head = self._outgoing.pop(0)
                        logger.trace("PikaPipelineThread - Thread TID:"
                                     f" {self.native_id} got the conditional."
                                     " Processing outgoing message.")
                        match head:
                            case ("msg", routing_key, body, exchange, props):
                                self.channel.basic_publish(
                                        exchange=exchange,
                                        routing_key=routing_key,
                                        properties=pika.BasicProperties(**props),
                                        body=body)
                            case ("ack", delivery_tag):
                                self.channel.basic_ack(delivery_tag)
                            case ("rej", delivery_tag, requeue):
                                self.channel.basic_reject(
                                        delivery_tag, requeue=requeue)
                            case ("fin",):
                                running = False
                                break
                            case ("syn", ev):
                                ev.set()
                            case ("zzz", duration):
                                time.sleep(duration)

                self._processing_complete(self._tick)
                self._tick += 1
        except BaseException as ex:
            if isinstance(ex, (
                    pika.exceptions.ChannelClosed,
                    pika.exceptions.ConnectionClosed)):
                # Using our channel or connection objects is no longer safe.
                # Clear them so we don't try to reuse their state
                self.clear()

            if threading.main_thread() == threading.current_thread():
                raise
            else:
                # Store the exception for now -- run_consumer will yield it
                # when the background thread stops
                self._shutdown_exception = ex
        finally:
            if self.has_channel:
                self._basic_cancel(consumer_tags)
            with self._condition:
                self._live = False
                self._condition.notify()

    def run_consumer(self):  # noqa: CCR001, E501 too high cognitive complexity
        """Receives messages from the registered input queues, dispatches them
        to the handle_message function, and generates new output messages. All
        Pika API calls are performed by the background thread."""

        if threading.main_thread() != threading.current_thread():
            raise ValueError(
                    "only the main thread can call PikaPipelineThread."
                    "run_consumer(); to execute a queue of Pika actions from"
                    " an arbitrary thread, call PikaPipelineThread.run()"
                    " instead")

        running = True
        old_handler = None

        def _handler(signum, frame):
            nonlocal running, old_handler
            running = False
            self.enqueue_stop()

            if callable(old_handler):
                old_handler(signum, frame)

        old_handler = signal.signal(signal.SIGTERM, _handler)

        self.start()

        try:
            while running and self.is_alive():
                method, properties, body = self.await_message(timeout=30.0)
                if method == properties == body is None:
                    continue
                try:
                    key = method.routing_key
                    dbd = json_utf8_decode(body)

                    for msg in self.handle_message(key, dbd):
                        match msg:
                            case (routing_key, message, exchange, headers):
                                self.enqueue_message(routing_key,
                                                     message,
                                                     exchange=exchange,
                                                     **headers)
                            case (routing_key, message):
                                self.enqueue_message(routing_key, message)

                    self.enqueue_ack(method.delivery_tag)
                    self.after_message(key, dbd)
                except RejectMessage as ex:
                    self.enqueue_reject(method.delivery_tag, requeue=ex.requeue)
        finally:
            self.enqueue_stop()
            self.join()
            signal.signal(signal.SIGTERM, old_handler)

            # Discard any requests that weren't processed (under the condition
            # lock for consistency's sake, but we are the only thread at this
            # point)
            with self._condition:
                logger.trace(f"PikaPipelineThread - Thread TID: {self.native_id}"
                             " clearing incoming queue.")
                self._incoming.clear()

            if self._shutdown_exception:
                raise Exception("Worker thread died unexpectedly") from self._shutdown_exception
