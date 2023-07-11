# Pipeline architecture

The `os2datascanner.engine2.pipeline` module contains the `engine2` pipeline,
also known as the _scanner engine_.

![Image of the interactions of os2datascanner components](pipeline-architecture.svg)

## What components make up the pipeline?

The pipeline implementation consists of five stages:

* the Explorer, which consumes a *source* message, explores all of the objects
  in that source, and produces potentially many *conversion* or *problem*
  messages;
* the Processor, which consumes a *conversion* message, converts an object into
  the appropriate form for a rule to be applied to it, and produces precisely
  one *representation* message, *problem* message, or *source* message;
* the Matcher, which consumes a *representation* message, attempts to match a
  rule against a representation of an object, and produces potentially many
  *match* messages and at most one *handle* message;
* the Tagger, which consumes a *handle* message, extracts useful metadata from
  the object that it references, and produces a *metadata* message; and
* the Exporter, which consumes *match*, *problem* and *metadata* messages and
  produces *result* messages suitable for the outside world.

![Overview of the data carried by OS2datascanner messages](pipeline-messages.svg)

To improve cache efficiency, and to reduce the amount of potentially sensitive
information transmitted over the underlying RabbitMQ message bus, the
Processor, Matcher and Tagger stages are customarily bundled into a single
process known as the _worker_.

## Components supporting the pipeline operation

In addition to the five stages mentioned above, there are also four _collectors_,
which update the databases for the admin and report modules with relevant information
about the running scanner jobs. While these _collectors_ are not technically a part of
the pipeline, they provide important information about the state of the running scanner
jobs across the admin and report modules:

* Checkup Collector (admin): This collects *checkup* messages about objects that should be
  revisited (scanned again) next time the scanner jobs runs.
* Status Collector (admin): This collects *status* messages about the current status of a
  scanner job, i.e. the number of objects scanned so far, the total number of objects,
  the number of explored sources, etc.
* Event Collector (report): This collector maintains `Organisation`s, `OrganizationalUnit`,
  `Account`, `Alias` and `Position` objects in the report module database, such as 
  bulk CRUD operations on said objects.
* Result Collector (report): This collects *problem*, *metadata* and *match* messages and
  is in charge of performing CRUD operations for `DocumentReport`s in the report module
  database.

## What are the pipeline's design principles?

* Simple external interfaces

  The pipeline should expose a clear API for getting instructions into the
  pipeline and results out of it; interacting with the pipeline in any other
  way should not be supported.

* Always in motion

  The pipeline (as a whole) should never wait. Individual instances of stages
  might wait for any number of reasons, but they shouldn't slow down the rest
  of the pipeline.

* High tolerance

  Provided that an AMQP message contains valid JSON, a stage should accept it
  immediately. Problems with handling the message should be presented as
  *problem* messages rather than raising an exception.

* Unambiguous results

  It should be possible, from the output of the pipeline, to distinguish
  between an object that didn't match a rule and an object that hasn't been
  examined yet. Objects in transit through the pipeline shouldn't just
  disappear.

* Trivial stage implementations

  Stages should be short and readable and should perform a single simple task.
  For example, the Tagger was added as a separate stage instead of giving the
  Matcher responsibility for metadata extraction.

* No unnecessary work

  Objects should skip over pipeline stages as soon as it's clear that it's
  possible.

* Clear security boundaries

  As many stages will be dealing with privileged authentication details and
  sensitive information, each stage should have clear security boundaries. To
  the extent that this is possible, a stage should be capable of being run as
  an unprivileged user with no network access in a read-only filesystem.

  Adding a new stage should be preferred to extending the security boundaries
  of an existing stage; this was another reason why Tagger, which requires
  access to content and metadata, was added instead of extending Matcher,
  which requires neither of these things.

* State is bad

  Stages should read JSON-formatted messages from AMQP queues, perform some
  appropriate work, and then write JSON-formatted messages to AMQP queues. No
  stage should maintain any internal (apart from trivial caching) or external
  state.

  In particular, this means that pipeline stages should not communicate with a
  database: their tasks should be precisely and exclusively specified by their
  input.

## The big picture - communication between OS2datascanner components

As mentioned, the engine consists of five stages that work in tandem with the
four collector processes and the admin and report module. This is a lot of complex,
moving parts.

To ease comprehension of the entire set of interactions at a fine devel of detail,
the complete, detailed interaction between all components (as well as the user) is illustrated by
the UML Sequence Diagram below:

![UML Sequence Diagram of engine component communication](./os2ds_current_pipeline_sequence.svg)

_Note: Due to the distributed nature of the system, all of the messages should be
considered asynchronous._

This diagram is divided into sections: one for each of the engine pipeline stages,
one for the collector processes with subsections, as well as two sections that briefly
describe startup and completion of a scanner job, respectively.

## The basis of a pipeline stage instance

Since every pipeline stage must communicate with RabbitMQ using AMQP and must be run
concurrently on separate threads, all engine stages share some common abstractions
depicted on the UML Class Diagram below:

![UML Class Diagram of general pipeline stage abstractions](./os2ds_queues.svg)

There are four classes in this class hierarchy, three of which that provide some general 
interactions with RabbitMQ:

- `PikaConnectionHolder`
- `PikaPipelineRunner`
- `PikaPipelineThread`

The `GenericRunner` handles messages that are specific to the OS2datascanner engine.

_Note: all of the four collector processes have their own specialized runner based
on `PikaPipelineThread` instead of using the `GenericRunner`._

Together, these three abstractions allows one to create a separate thread for some routine
that involves communication with an AMQP message broker. Let's us examine each one in detail:

### `PikaConnectionHolder`

This class is responsible for establishing and maintaining a blocking connection with an AMQP broker
with parameters defined in `os2datascanner/utils/pika_settings.py`.
These parameters include host, port, virtual_host, heartbeat and authentication with credentials
among others.

It can also create an AMQP channel and automatically takes care of any required cleanup upon object
destruction. In other words, if we consider AMQP connections and channels to be resources,
`PikaConnectionHolder` implements [RAII](https://en.wikipedia.org/wiki/Resource_acquisition_is_initialization) for said resources.

### `PikaPipelineRunner`

This class extends `PikaConnectionHolder` with AMQP exchange and queue declarations as well as
wrapper methods for basic AMQP messages such as acknowledgement, consumption and cancellation.

### `PikaPipelineThread`

This class implements `threading.Thread` as well as extending `PikaPipelineRunner`. 
It runs two threads: a main thread (`run_consumer()`) and a background thread (`run()`).

The background thread runs an event-loop that reads from a local message buffer 
(`self._outgoing`) and dispatches these to RabbitMQ depending on the message head.

The main thread runs another event-loop that reads from a local message buffer
(`self._incoming`), which contains the read queues. It produces messages for the background
thread using the `handle_message()`-method.
