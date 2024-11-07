# Pre-execution of rules (SmartDelta)

This document describes the OSdatascanner functionality that lets `Source`s
speculatively pre-execute rules to drastically improve scan performance. (In
customer-facing materials, this function is called "SmartDelta").

As this function has a significant impact on the performance of scanner jobs,
the ![](smartdelta.png) icon is displayed in the administration system's UI
when a given scanner type supports it.

(If you haven't already done so, you may want to read `engine2.md` and
`rules.md` for an introduction to the concepts used here.)

## Rules do everything

Unlike most systems, OSdatascanner doesn't distinguish between filters and
search terms: everything that inspects an object and makes a decision about
it is implemented as a rule that returns matches. (The report module conceals
this fact by treating only certain rules as "suitable for display", but
behind the scenes a typical file with visible matches will also have matched
lots of other, hidden rules.)

Even some of the core functionality that you might _think_ of as filtering,
like the Last-Modified date check, is implemented in this way: if you scan
using a `RegexRule` and tick the _Check last modification timestamp_ box,
the engine receives and executes a
`AndRule(LastModifiedRule(...), RegexRule(...))` combination rule.

On the one hand, this is clever, flexible and powerful -- one person's
hidden filter is another person's interesting match, and making everything
work in the same way means that the engine doesn't privilege some checks
over others. If you _want_ to use the OSdatascanner engine (through the API
server, say) to find all images in your website bigger than 1920x1080 and to
tell you how big they are, you can, even if the report module doesn't choose
to show those results.

On the other, though, this means a lot of overhead, and overhead means a
performance burden. Imagine for a moment a file server with 1,000,000 files,
and we want to scan all of the files modified since the last scan; even
if there are only 1,000 such files, we still need to generate a million
RabbitMQ messages, serialise them, compress them, put them into message
queues, read them, decompress them, deserialise them, compute modification
dates for them... even a total time expenditure of just five milliseconds per
file would mean almost an hour and a half of unnecessary work. That's quite
a big price to pay for flexibility.

## Pre-execution of rules

OSdatascanner's solution to this problem is to let `Sources` take a sneak
peek at the `Rule` that's being executed _during the exploration process_, so
they can enumerate only the files that have a chance of matching the `Rule`.

To see how this works, let's implement a simple source exploration strategy
for a generic API.

```python
class APISource(Source):
    # ...

    def handles(self, sm: SourceManager):
        api_client = sm.open(self)

        for page in api_client.get_pages(per_page=50):
            for object in page:
                yield APIHandle(self, object.path)
```

This exploration strategy suffers from the performance challenge we mentioned
above: the rest of the pipeline will have to inspect every `APIHandle` we spit
out, even if it might quickly be dismissed by a `LastModifiedRule`.

Let's implement some trivial pre-execution logic to fix that:

```python
class APISource(Source):
    # ...

    def handles(self, sm: SourceManager, *, rule=None):
        api_client = sm.open(self)

        cutoff: datetime.datetime | None = None
        if rule:
            # See if the first thing being executed is a LastModifiedRule
            first, pve, nve = rule.split()
            if isinstance(first, LastModifiedRule):
                # It is! Let's extract the date from it and filter out anything
                # older than that
                cutoff = first.after

        for page in api_client.get_pages(per_page=50):
            for object in page:
                if not cutoff or object.last_changed > cutoff:
                    yield APIHandle(self, object.path)
```
The scanner engine will automatically detect that `APISource.handles` supports
the `rule` parameter, and will use it to pass the rule being executed into the
exploration strategy. And that's it! A few lines of code later and our `Source`
is dramatically more efficient to scan.

### Help with analysis

In the toy example above, we split the input rule up ourselves using the
`split()` function. What do we do if the rule we want to pre-execute is more
deeply nested inside a complex rule?

Exploration strategies can, in principle, do whatever they want here (they get
a complete `Rule`, after all, and can take it apart however they like), but
there's also a small library of utility functions in the
`os2datascanner.engine2.rules.utilities.analysis` package that implements some
common analyses.

#### `compute_mss`

The `compute_mss()` function takes a rule and computes its "minimal
`SimpleRule` set": that is, all the concrete `SimpleRule`s that _must_ be run
to arrive at a positive conclusion.

```python
>>> from os2datascanner.engine2.rules.utilities.analysis import compute_mss
>>> compute_mss(
...     AndRule("last-modified", "CPR number",
...             OrRule(
...                 AndRule("name", "address"),
...                 AndRule("name", "telephone number"))))
{'name', 'last-modified', 'CPR number'}
```

This function can decompose logical rules in a moderately sophisticated way:
for example, it can tell that every branch of the required `OrRule` includes
`"name"` as a requirement.

### What makes sense to pre-execute?

The _Check last modification timestamp_ function is a good example of a
basically free check of a lightweight property that can be used to skip lots of
unnecessary work. Depending on the `Source`, there may (or may not!) be others.
If the rules query a database, for example, we might even want to pre-run
those queries:

```python
class DBSource(Source):
    # ...

    def handles(self, sm: SourceManager, *, rule=None):
        db_ctx = sm.open(self)

        query_obj = db_ctx.table["SomeTable"].objects.all()

        for component in compute_mss(rule):
            if isinstance(component, DatabaseTestRule):
                column, operator, value = component.parts
                query_obj = query_obj.where(column, operator, value)

        for object in db_ctx.execute(query_obj):
            yield DBHandle(self, object.pk, row=object)
```

Doing this basically turns an OSdatascanner rule into an unusual representation
of a SQL query, which means that we can write them to make optimal use of a
database index (or add a new database index for the rule we want to execute).

Remember, though, that the point of this mechanism is that it doesn't have to
be _perfect_. Every rule you pre-evaluate is another bit of filtering that
reduces the burden on the message bus, but the end result should always be the
same: running a scan with and without pre-filtering should find the same
matches in the end, even if many more objects get inspected without it.
