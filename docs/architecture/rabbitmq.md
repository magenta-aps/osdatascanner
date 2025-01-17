# RabbitMQ in OS2datascanner

In order to obtain a distributed system, where the admin module, the report module
and the engine components can run concurrently on separate machines that are
part of a network, [RabbitMQ](https://www.rabbitmq.com) (with [AMQP](https://www.amqp.org/) version 0.9.1)
is used as the primary medium of communication between said modules/components.


## Communication between engine components and RabbitMQ

Almost all messages are routed through the 
[RabbitMQ default exchange](https://www.cloudamqp.com/blog/part4-rabbitmq-for-beginners-exchanges-routing-keys-bindings.html),
using the `routing_key` to determine the destination queue. The exception being a fanout exchange 
called "broadcast" used by some OSdatascanner components to send and receive global messages.

By default, message queues have the prefix 'os2ds_' which is then followed by the type of messages that are 
stored in the queue (e.g. the queue `os2ds_scan_specs` contains `ScanSpecMessage`s and so on).
A queue should only contain one type of message at all times.

## Dynamic message consumption & routing_key designation
**If you're going to use this functionality, it's important to
read the next under-section too, about its ties to the admin module. One without the other will
most likely result in undesirable behaviour.**

By default, what you've read so far is true: messages will go through `os2ds_` prefixed queues. 
But, two of the Engine2 pipeline's processes have support for dynamically 
creating and prioritizing message queues. More specifically: the `explorer` and the `worker`.

Currently, with emphasis on differentiating between full- and delta-scans, allowing these to run 
in parallel - but it can also be used to define who shares explorer and worker resources 
in a multi tenant environment. 


The explorer and worker services support an environment variable: `QUEUE_PRIORITY`

For example, for a worker, you might add: 

`- QUEUE_PRIORITY=conversions_delta conversions_full os2ds_conversions`

These values will be used to declare the RabbitMQ queues (actually creating them on service start) 
and, in order of insertion, be what queues are preferred to consume from.

* _Do note that here `os2ds_conversions` is included, as it's our default queue, but it
isn't necessary if you're running a new installation, or if you're absolutely 
sure its empty when configuring._

In the case above, `conversion_delta` will be 1st priority and as so, 
the `worker` will never cancel its _consumer_ for this queue. 
Consumers for `conversions_full` and `os2ds_conversions` will be started 
and cancelled in prioritized order, depending on how many messages are in queue. The first priority
queue must be empty before we start consuming from any of the lower priority ones - and only from 
one of them at a time. If a message enters a higher priority queue than our current priority,
we'll cancel the lower priority consumer.

This behaviour is currently introduced in `run_stage.py`, where we're hooking into the 
`_processing_complete` method. All this does is, if we're running a `worker` or an `explorer`,
we'll call the method `_check_and_switch_priority` every 5 seconds. 
(This means that priority switches may not be immediate, but close enough, right?).

`_check_and_switch_priority` is pretty much just a match-case method that enforces the behaviour just described - checking queue message counts and figuring out what consumers to run/cancel.


### Ties to the admin module

The `Client` model defines four fields of relevance to the message routing, namely:

```python
    explorer_delta_queue = models.TextField(
        default="os2ds_scan_specs",
    )
    explorer_full_queue = models.TextField(
        default="os2ds_scan_specs",
    )
    conversion_delta_queue = models.TextField(
        default="os2ds_conversions"
    )
    conversion_full_queue = models.TextField(
        default="os2ds_conversions"
    )
```

These fields are used to populate `ScanSpecMessage`'s, which allows us to send messsages
to our desired RabbitMQ conversion & explorer queue(s) when starting a scan, and throughout the
engine2 pipeline.
By default, these are set to `os2ds_conversions|os2ds_scan_specs` - and so is the defaults 
of `ScanSpecMessage`. This is for backwards compatibility as well as having the system work out
the box, granted, with no parallelization of full|delta scans or multi-tenant resource assignment.

The key takeaway is that you **must** make sure that these fields and `QUEUE_PRIORITY` align. 

`Client`'s fields are about populating queues and `QUEUE_PRIORITY`
is about _actually creating_ queues and consuming from them.
You can't publish messages to queues that don't exist, 
and you can't get rid of messages without having something to consume them.


You may now see how this could be used for multi tenancy - or, there are multiple patterns, 
depending on what you're trying to achieve.

To share worker resources between two customers, you could configure two `Client`'s 
(Vejstrand & Magenta) like so:


```python
# VEJSTRAND
    conversion_delta_queue = conversions_delta_vejstrand
    conversion_full_queue = conversions_full_vejstrand
```

```python
# MAGENTA
    conversion_delta_queue = conversions_delta_magenta
    conversion_full_queue = conversions_full_magenta
```

And then define two workers with `QUEUE_PRIORITY`:

```python
# Worker 1
- QUEUE_PRIORITY=conversions_delta_vejstrand conversions_full_vejstrand conversions_delta_magenta conversions_full_vejstrand
```

```python
# Worker 2
- QUEUE_PRIORITY=conversions_delta_magenta conversions_full_vejstrand conversions_delta_vejstrand conversions_full_vejstrand 
```

.. or some other pattern, suiting your needs.

F.e., it's also a possibility to share RabbitMQ queues and group `Client` field definitions instead.
You might figure out that 2 `Client`s can share the same delta queue, "FIFO" style:

```python
# VEJSTRAND
    conversion_delta_queue = conversions_delta
    conversion_full_queue = conversions_full_vejstrand
```

```python
# MAGENTA
    conversion_delta_queue = conversions_delta
    conversion_full_queue = conversions_full_magenta
```


