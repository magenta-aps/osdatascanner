# RabbitMQ in OSdatascanner

In order to obtain a distributed system, where the admin module, the report module
and the engine components can run concurrently on separate machines that are
part of a network, [RabbitMQ](https://www.rabbitmq.com) (with [AMQP](https://www.amqp.org/) version 0.9.1)
is used as the primary medium of communication between said modules/components.


## Communication between engine components and RabbitMQ

Almost all messages are routed through the 
[RabbitMQ default exchange](https://www.cloudamqp.com/blog/part4-rabbitmq-for-beginners-exchanges-routing-keys-bindings.html),
using the `routing_key` to determine the destination queue. The exception being a fanout exchange 
called "broadcast" used by some OSdatascanner components to send and receive global messages.

By default, most message queues have the prefix 'os2ds_' which is then followed by the type of messages that are 
stored in the queue (e.g. the queue `os2ds_scan_specs` contains `ScanSpecMessage`s and so on).
A queue should only contain one type of message at all times.

## Dynamic queue subscription and prioritization

`worker` and to some extent `explorer` can also dynamically declare queues
and shift consumer focus between them. There are two related mechanisms:

* **Per-scan conversion queues**, where each scannerjob gets its own dedicated
  conversion queue that is created when the scan starts and deleted when it
  finishes (or is cancelled).
* **Static-named queue prioritization** via the `QUEUE_PRIORITY` env var,
  which lets a worker or explorer prefer one named queue over another.

The two mechanisms can be used together. The per-scan queue model is the
primary route for conversion messages today; the `QUEUE_PRIORITY` mechanism
is still in use for explorer queues and remains supported for legacy setups.

### Per-scan conversion queues

When a scan job starts, the admin module:

1. Computes a queue name of the form `osds_conversions.{scanner_pk}_{YYYYMMDDTHHMMSS}`
   from the scanner PK and the scan start time (see `_per_scan_queue_name` in
   `scanner_helpers.py`).
2. Stores it on the new `ScanStatus` row (`conversion_queue_name`) along with
   the scan-type tag (`conversion_queue_tag`, either `"full"` or `"delta"`).
3. Calls `notify_new_conversion_queue`, which declares the queue on the broker
   and sends a `CommandMessage` with `new_queue=...` and `new_queue_priority=...`
   through the `broadcast` fanout exchange.

Workers receive that broadcast on their anonymous command queue and, via
`new_queue_hook` in `worker.py`, subscribe to the named per-scan queue (if
the queue's tag passes their `CONVERSION_PRIORITY` filter - more on that below).
Other stage types (explorer, exporter, collectors) ignore `new_queue`
broadcasts; they don't speak ConversionMessage.

When the scan finishes, the status collector calls `delete_per_scan_queue`,
which broadcasts a `delete_queue` `CommandMessage` *first* and only then
deletes the queue on the broker. 

Cancellation goes through the same path, except that
`cancel_scan_tag_messages(..., delete_queue=True)` first broadcasts an `abort`
to stop in-flight processing, and then deletes the queue. The broker discards
every remaining message in one operation.

#### Restart safety

Per-scan queues are discovered through broadcasts. If a worker restarts
mid-scan, it would otherwise miss every queue announced before it started.
Two mechanisms close that gap:

* On startup, every worker emits a `worker_hello` `CommandMessage` containing
  the name of its own anonymous command queue. The status collector listens
  for `worker_hello` and replies _directly_ to that anonymous queue with one
  `new_queue` message per active scan.
* As an extra safety net, the status collector also re-broadcasts every active
  scan's queue name every 600 tick.

#### `CONVERSION_PRIORITY`

The worker service supports an environment variable: `CONVERSION_PRIORITY`

`- CONVERSION_PRIORITY=delta full`

The values are _tags_, not queue names: each value must be either `"full"` or
`"delta"` (matching the `conversion_queue_tag` set on the ScanStatus). The
first entry is the highest priority. Workers only consume per-scan queues
whose tag is in this list, and prefer queues with the higher-priority tag
when there's work for both - falling back to lower-priority tags only when
the preferred ones have nothing to deliver.

A typical setup with two workers could look like this:

```yaml
worker_0:        # full-scan-biased
  - CONVERSION_PRIORITY=full delta
worker_1:  # delta-scan-biased
  - CONVERSION_PRIORITY=delta full
```

Both workers see all per-scan queues, but each focuses on the type of scan
it was assigned to handle. The bias is re-evaluated every 50 tick
(`tick_hook` → `_check_per_scan_priority`), so a worker may continue
processing a lower-priority queue for while after
higher-priority work arrives.

### Static-named queue prioritization

This is the older mechanism, but it's still in use for explorer queues and
remains supported for conversion queues in legacy setups (see
[Ties to the admin module](#ties-to-the-admin-module) below).

**If you're going to use this functionality for conversion queues, it's
important to read the next under-section too, about its ties to the admin
module. One without the other will most likely result in undesirable
behaviour.**

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

> **Note:** the `Client.conversion_delta_queue` and `Client.conversion_full_queue`
> fields described in this section are on their way out. Conversion routing
> has moved to per-scan queues (see above), and these two fields are kept for
> backwards compatibility with installations that have not yet migrated. New
> installations should leave them at their defaults. The explorer queue
> fields remain in use.

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


