# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for putting a message down and picking it up again later: the backoff
bookkeeping, and whether a deferred message actually finds its way back.

The round trip is mostly a claim about how RabbitMQ behaves rather than about
code: a message published to a headers exchange selects a delay queue by header
while its routing key is left alone, and when it expires the dead-letter hop
routes it by that untouched routing key back to the queue it started in. If any
part of that is wrong, deferred objects are silently dropped and never scanned,
so it is tested against a real broker."""

import json
import time

import pytest

from os2datascanner.engine2 import settings
from os2datascanner.engine2.pipeline.utilities import deferral

pika = pytest.importorskip("pika")


DELAY_MS = 1500
TARGET_QUEUE = "os2ds_test_deferral_target"


@pytest.fixture
def deferral_config():
    """Pins the backoff so the tests do not depend on whatever the deployment
    happens to be configured with."""
    conf = deferral._conf()
    saved = dict(conf)
    conf.update({
        "backoff_ms": [1000, 2000, 5000],
        "max_deferral_ms": 10000,
    })
    yield conf
    conf.clear()
    conf.update(saved)


class TestNextDeferral:
    def test_first_deferral_uses_the_first_delay(self, deferral_config):
        delay, body = deferral.next_deferral({"handle": "x"})

        assert delay == 1000
        assert body[deferral.DEFERRAL_KEY] == {
                "attempts": 1, "waited_ms": 1000}

    def test_no_delays_configured_means_no_deferral(self, deferral_config):
        """Configuring no delays is how an operator switches waiting off, and
        everything else in this feature answers a misconfiguration by getting on
        with the conversion rather than by failing."""
        deferral_config["backoff_ms"] = []

        assert deferral.next_deferral({"handle": "x"}) is None

    def test_the_original_body_is_not_modified(self, deferral_config):
        """The body has to be republished with the bookkeeping added, but the
        caller's copy is still used for logging and accounting."""
        original = {"handle": "x"}
        deferral.next_deferral(original)

        assert original == {"handle": "x"}

    def test_backoff_grows(self, deferral_config):
        body = {"handle": "x"}
        delays = []
        for _ in range(3):
            plan = deferral.next_deferral(body)
            if plan is None:
                break
            delay, body = plan
            delays.append(delay)

        assert delays == [1000, 2000, 5000]

    def test_the_last_delay_repeats(self, deferral_config):
        """Past the end of the list the wait settles into a steady poll rather
        than growing without bound."""
        body = {deferral.DEFERRAL_KEY: {"attempts": 9, "waited_ms": 0}}

        delay, _ = deferral.next_deferral(body)

        assert delay == 5000

    def test_deferral_stops_once_the_budget_is_spent(self, deferral_config):
        """Otherwise an object waiting for something that never comes would be
        deferred forever and never scanned at all."""
        body = {deferral.DEFERRAL_KEY: {"attempts": 1, "waited_ms": 9000}}

        assert deferral.next_deferral(body) is None

    def test_a_whole_run_of_deferrals_terminates(self, deferral_config):
        """Whatever the configuration, deferring must not be able to loop
        forever."""
        body = {"handle": "x"}
        for _ in range(100):
            plan = deferral.next_deferral(body)
            if plan is None:
                return
            _, body = plan
        pytest.fail("deferral never gave up")


class TestQueueNaming:
    def test_queues_are_named_after_their_delay(self, deferral_config):
        """A queue's message TTL is fixed when it is declared, so a changed
        backoff has to name new queues rather than clash with the old ones."""
        assert deferral.queue_name(1000) != deferral.queue_name(2000)
        assert deferral.queue_name(1000).endswith("1000")


class TestPublication:
    def test_the_routing_key_is_left_alone(self):
        """It is the routing key that brings the message back, so the delay queue
        has to be selected by something else."""
        routing_key, body, exchange, properties = deferral.publication(
                "osds_conversions.17_20260814T080000", 1500, {"handle": "x"})

        assert routing_key == "osds_conversions.17_20260814T080000"
        assert body == {"handle": "x"}
        assert exchange == deferral.DEFERRAL_EXCHANGE
        assert properties["headers"] == {deferral.DEFERRAL_HEADER: "1500"}


@pytest.fixture
def channel():
    conf = settings.amqp
    parameters = pika.ConnectionParameters(
            host=conf["AMQP_HOST"],
            credentials=pika.PlainCredentials(
                    conf["AMQP_USER"], conf["AMQP_PWD"]),
            socket_timeout=5, connection_attempts=2)
    try:
        connection = pika.BlockingConnection(parameters)
    except Exception:
        pytest.skip("no AMQP broker reachable")

    ch = connection.channel()
    yield ch

    # Leave nothing behind: these queues are not part of the pipeline.
    for queue in (TARGET_QUEUE, deferral.queue_name(DELAY_MS)):
        try:
            ch.queue_delete(queue)
        except Exception:
            pass
    connection.close()


@pytest.fixture
def topology(channel):
    """Declares the same topology the worker declares, for one short delay."""
    channel.exchange_declare(
            deferral.DEFERRAL_EXCHANGE,
            exchange_type="headers", durable=True, auto_delete=False)

    delay_queue = deferral.queue_name(DELAY_MS)
    channel.queue_declare(
            delay_queue, durable=True, exclusive=False, auto_delete=False,
            arguments={
                "x-message-ttl": DELAY_MS,
                "x-dead-letter-exchange": "",
            })
    channel.queue_bind(
            exchange=deferral.DEFERRAL_EXCHANGE, queue=delay_queue,
            arguments={
                "x-match": "all",
                deferral.DEFERRAL_HEADER: str(DELAY_MS),
            })

    # Stands in for a per-scan conversion queue.
    channel.queue_declare(TARGET_QUEUE, durable=True)
    channel.queue_purge(TARGET_QUEUE)
    channel.queue_purge(delay_queue)

    return delay_queue


def defer(channel, body, delay_ms=DELAY_MS, target=TARGET_QUEUE):
    """Publishes exactly as the worker does when it stands down from a claim."""
    channel.basic_publish(
            exchange=deferral.DEFERRAL_EXCHANGE,
            routing_key=target,
            body=json.dumps(body).encode(),
            properties=pika.BasicProperties(
                    delivery_mode=2,
                    headers={deferral.DEFERRAL_HEADER: str(delay_ms)}))


def drain(channel, queue, timeout=6.0):
    """Waits for one message on a queue, returning its decoded body or None."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        method, _, body = channel.basic_get(queue, auto_ack=True)
        if method is not None:
            return json.loads(body)
        time.sleep(0.2)
    return None


class TestDeferralRoundTrip:
    def test_a_deferred_message_comes_back_to_its_origin_queue(
            self, channel, topology):
        """The whole mechanism in one test: held for its delay, then returned to
        the queue it came from."""
        defer(channel, {"handle": "report.pdf", "dedup_deferral":
                        {"attempts": 1, "waited_ms": DELAY_MS}})

        # It must not be available immediately, or the worker would spin on it.
        assert channel.basic_get(TARGET_QUEUE, auto_ack=True)[0] is None

        returned = drain(channel, TARGET_QUEUE)

        assert returned is not None, "deferred message never came back"
        assert returned["handle"] == "report.pdf"
        # The bookkeeping survives the trip, which is what stops the object
        # being deferred forever.
        assert returned["dedup_deferral"] == {
                "attempts": 1, "waited_ms": DELAY_MS}

    def test_the_message_waits_in_the_delay_queue(self, channel, topology):
        """Routing by header has to put the message in the delay queue rather
        than delivering it straight to the routing key's queue."""
        defer(channel, {"handle": "report.pdf"})
        time.sleep(0.3)

        assert channel.queue_declare(
                topology, passive=True).method.message_count == 1

    def test_an_unmatched_header_is_not_routed(self, channel, topology):
        """A headers exchange drops what it cannot match. If a delay queue for
        the configured backoff were missing, deferred objects would vanish, so
        this documents that the worker must declare a queue for every delay it
        is willing to use."""
        defer(channel, {"handle": "report.pdf"}, delay_ms=999999)
        time.sleep(0.3)

        assert channel.queue_declare(
                topology, passive=True).method.message_count == 0
        assert channel.basic_get(TARGET_QUEUE, auto_ack=True)[0] is None
