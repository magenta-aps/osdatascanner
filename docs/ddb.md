# Direct database scans

This document is a combined case study and tutorial describing how we added a
database data source without an API to OSdatascanner. This is not generally
recommended, as it skips application-level constraints and security checks
that may be part of the data source's security guarantees, but it may sometimes
be necessary for searching certain specialised systems.

(If you haven't already, you may wish to read [the general documentation for
the scanner engine](engine2.md) and [the detailed discussion of rules](rules.md)
before continuing.)

## The problem

One of our partners asked us if OSdatascanner could be made to scan the
[SBSYS case management system](https://sbsys.dk/), widely used throughout the
Danish public sector. SBSYS is a family of .NET applications and modules
running atop, and tightly coupled to, a number of Microsoft SQL Server
databases.

The ownership and architecture of the SBSYS system is complex. [The Danish
municipalities and regions that use the system](https://sbsys.dk/index.php/medlemmer/),
covering roughly 35% of the Danish population[^1], hold the rights to it
through a voluntary association, _Brugerklubben SBSYS_ (the SBSYS Users' Club),
but they contract its development, support and maintenance out to private
companies. As a result, the ecosystem is a bit of a patchwork: many different
developers have built different APIs for the bits of the system their own
extensions care about, but the system as a whole seems not oo have been
designed with a unified API in mind.

(A REST API for the database, known as the WebAPI, _has_ been retrofitted onto
the system, but our partner explicitly warned us away from it due to serious
performance issues.)

The source code of the SBSYS system is also not freely available; the
association treats it as a collectively-owned proprietary system, and it only
shares its code (and documentation!) with the companies contracted to provide
services to the association. The only information our partner was able to
provide us with was the system's database schema and some explanatory remarks
for it.

[^1]: As of April 2025.

## Our approach

So, we had a system that functionally had no API and (at least as far as we
were concerned) very limited documentation. How did we begin?

### Starting principles

As far as possible, we wanted to avoid making changes to the architecture of
the OSdatascanner scanner engine for the sake of SBSYS. A SBSYS data source
would ideally behave like any other: it would produce `Handle`s that refer to
cases in the system, and these could be explored further to find text comments
and files attached to those cases.

```python
# pseudocode, but close enough
class SBSYSDBSource(engine2.core.Source):
    def _generate_state(self):
        with DatabaseConnection(...) as db:
            yield db.cursor()

    def handles(self, sm):
        cursor = sm.open(self)

        for case in cursor.select("*", from='Case', batch_size=2000):
            yield SBSYSDBCase(self, case["ID"], case["Title"])
```

!!! note
    The columns of the SBSYS database are _actually_ named using a mixture of
    English, Danish, and Danish with spelling errors, but for the purposes of
    this documentation we're just going to pretend everything is in English.

It should also be possible for the user to build their own scanner rules, just
as they can for other OSdatascanner data sources: we don't want the source to
only support a handful of complex rules implemented by hand by us in Python.

### The database abstraction

That meant that we needed a database abstraction that could communicate with
SQL Server and return the results as Python objects. Luckily, that's what
[SQLAlchemy](https://www.sqlalchemy.org/) gave us.

SQLAlchemy has a few operating modes: it can provide a full ORM, with Python
classes representing database tables and objects representing database rows,
or it can work as a simple database abstraction layer, returning tuples and
dictionaries. For flexibility's sake, and because we don't know how often the
definition of the underlying database is changed, we picked the latter.

Even in this simpler mode, SQLAlchemy can still use runtime introspection to
build a Python-level representation of the database, letting us see and work
with its structure:

```python
>>> engine = create_engine(
...         "mssql+pymssql://admin:password@db-server:1433/SbSysNetDrift")
>>> metadata_obj = MetaData()
>>> metadata_obj.reflect(bind=engine, only=("Case", "User", "Person",))
# a few seconds go by
>>> metadata_obj.tables.keys()
dict_keys(['Case', 'PlaceOfEmployment', 'Address', 'CaseType', 'CaseStatus',
           'CaseStateReference', 'User', 'Office', 'CaseParty',
           'CasePartyTypeReference', 'CasePartyRole', 'Person',
           'CivilRegistryStatus'])
```

The introspection code is smart enough to also include the other tables
referenced by the three tables we asked for: `User`s have `Address`es and are
associated with an `Office`, `Person`s also have a home `Address` and have a
reference to a `CivilRegistryStatus`, and so on.

!!! note
    Introspection takes time; if we hadn't given specific tables in the `only=`
    parameter, importing a database would take minutes rather than seconds.
    It's a good idea to use as few tables as possible. (And anyway, it's easy
    to add more later.)

```python
>>> Case = tables["Case"]
>>> type(Case)
<class 'sqlalchemy.sql.schema.Table'>
>>> pprint.pprint(list(Case.c)[0:7])
[Column('ID', INTEGER(), table=<Case>, primary_key=True, nullable=False,
        server_default=Identity(start=1, increment=1)),
 Column('CaseUUID', UNIQUEIDENTIFIER(), table=<Case>, nullable=False,
        server_default=DefaultClause(
                <sqlalchemy.sql.elements.TextClause object at 0x74b356eb30d0>,
                for_update=False)),
 Column('Number', NVARCHAR(length=50, collation='SQL_Danish_Pref_CP1_CI_AS'),
        table=<Case>, nullable=False),
 Column('Title', NVARCHAR(length=450, collation='SQL_Danish_Pref_CP1_CI_AS'),
        table=<Case>, nullable=False),
 Column('IsProtected', BIT(), table=<Case>, nullable=False,
        server_default=DefaultClause(
                <sqlalchemy.sql.elements.TextClause object at 0x74b356e31610>,
                for_update=False)),
 Column('CaseworkerID', INTEGER(), ForeignKey('User.ID'), table=<Case>,
        nullable=False),
 Column('MunicipalityID', INTEGER(), ForeignKey('Municipality.ID'),
        table=<Case>, nullable=False),
 Column('LastChanged', DATETIME(), table=<Case>,
        server_default=DefaultClause(
                <sqlalchemy.sql.elements.TextClause object at 0x74b356e04ed0>,
                for_update=False)),
 ]
```

!!! warning
    Note the presence of the `IsProtected` flag in the `Case` table. This is an
    application-level constraint: OSdatascanner (through its raw database
    connection) will be able to read protected and unprotected cases alike.

    This is a good example of why you might _not_ want to use direct
    database access, if you can avoid it: the pairing of a database and an
    access control layer gives you meaningfully more security.

This representation can also be used to make database queries, which is what
we needed for our `handles()` implementation:

```python
>>> with engine.connect() as c:
...     result = c.execute(Case.select())
...     print(result.fetchone())
...
(1, UUID('2b37af33-bdfc-4c9b-b332-cae56310e963'), '12.34.56-L01-2-34',
 'Construction of a new playground', True, 17,
 datetime.datetime(2023, 9, 11, 9, 17, 24), ...)
```

### Handling rule execution

OK, that took care of getting the data out of the database. So far so good. The
next step was getting that data to our rule engine so we could search it for
issues.

We had two potentially competing objectives here:

* the user should be able to build an arbitrary rule up instead of just letting
  them pick from a handful that we've implemented specially; but
* the scan needed to have acceptable performance, even though we'd be digging
  through a database...
    * potentially used to track every official task...
        * for the last several decades...
            * by a large municipality...
                * in Denmark, a country with a big public sector.[^2]

[^2]: According to Statistics Denmark, just over [three in ten people
were employed in public administration, education and health](https://www.statistikbanken.dk/xls/247796)
as of 2023.

The first of these was the easiest one to accommodate in the OSdatascanner
architecture. We defined a new rule type that operated on database fields:

```python
>>> rule1 = SBSYSDBRule("Title", "icontains", "Playground")
>>> rule2 = SBSYSDBRule("LastChanged", "lte", "2025-01-01T00:00:00Z")
>>> combination = AndRule(rule1, rule2)
```

These rules have an obvious Python interpretation
(`lower("Playground") in lower(row["Title"])` and
`row["LastChanged"] <= datetime.datetime(2025, 1, 1, 0, 0)` respectively), so
the scanner engine's half of the work is already done. But what if we could
also communicate these constraints to the database, so we could filter out all
the rows that wouldn't match them before the rule engine gets involved? Then
we'd meet our second objective too.

SQLAlchemy proved to be a very good tool for this. Its `Column` objects have
many methods and overloaded operators that you can use to build SQL expression
fragments up, and you can join these to a `select()` expression by using its
`where()` method:

```python
>>> expr1 = Case.c.Title.icontains("playground")
>>> expr2 = Case.c.LastChanged < datetime.datetime(2025, 1, 1, 0, 0)
>>> combination = and_(expr1, expr2)
>>> print(Case.select().where(combination))
SELECT "Case"."ID", "Case"."CaseUUID", "Case"."Number", "Case"."Title",
       "Case"."IsProtected", "Case"."CaseworkerID", "Case"."LastChanged", ...
FROM "Case"
WHERE (lower("Case"."Title") LIKE '%' || lower(:Title_1) || '%')
AND "Case"."LastChanged" < :LastChanged_1
```

So that's what we did! We implemented a conversion process that translates a
OSdatascanner `Rule` into a SQLAlchemy `ColumnExpression`, allowing the
database to do most of the heavy lifting. (Doing this translation has another
big benefit: if you want a `Rule` to be evaluated even faster, you can just
create a database index that optimises the query that it gets translated into.)

(It's not a coincidence that this technique is also described in
[the documentation for pre-execution of rules](smartdelta.md#what-makes-sense-to-pre-execute):
although we hadn't actually encountered a database that needed scanning at that
point, the potential relationship between `Rule`s and SQL was already clear,
and it was very satisfying to see how directly it worked.)

### Cross-table expressions

Sometimes you want to be able to write a rule that stretches across multiple
tables: to be able to say, for example, "show me all `Case`s associated with a
`User` whose `EmploymentStatus` has a `Name` that contains `inactive`".

Doing this with SQLAlchemy is easy and very mechanical. All we need to do is
to walk that compound expression and translate it bit-by-bit into a constraint:

```python
>>>        # Show me all cases...
>>> expr = Case.select().where(
...          # ... whose Caseworker can be connected to a User...
...     and_(Case.c.CaseworkerID == User.c.ID,
...          # ... who can be connected to an EmploymentStatus...
...          User.c.EmploymentStatusID == EmploymentStatus.c.ID,
...          # ... the name of which includes "inactive"
...          EmploymentStatus.c.Name.icontains("inactive")))
```

We implemented a simple dot-separated expression parser that does this
mechanical translation automatically, so we can just write the rule directly:

```python
>>> rule = SBSYSDBRule(
...         "Caseworker.EmploymentStatus.Name", "icontains", "inactive")
```

#### ... with soft foreign keys

This expression parser takes advantage of the fact that SQLAlchemy
introspection gives us information about the target of a foreign key relation.
Remember this from earlier?

```python
 Column('CaseworkerID', INTEGER(), ForeignKey('User.ID'), table=<Case>,
        nullable=False),
```

This column object has a `foreign_keys` property that contains a reference to
the `User` table, so we know that following `Caseworker` takes us to a `User`,
and that following `User.EmploymentStatus` takes us in turn to an
`EmploymentStatus`.

Unfortunately, not all SBSYS relations are so straightforward. `Case.Party`,
for example, is a reference to a `CaseParty` object, which contains a "soft"
foreign key:

```python
>>> pprint(list(tables["CaseParty"].c))
[Column('ID', INTEGER(), table=<CaseParty>, primary_key=True, nullable=False,
        server_default=Identity(start=1, increment=1)),
 Column('CaseID', INTEGER(), ForeignKey('Case.ID'), table=<CaseParty>,
        nullable=False),
 Column('PartyType', INTEGER(), ForeignKey('CasePartyTypeReference.ID'),
        table=<CaseParty>, nullable=False),
 Column('PartyID', INTEGER(), table=<CaseParty>, nullable=False),
 Column('CasePartyRoleID', INTEGER(), ForeignKey('CasePartyRole.ID'),
        table=<CaseParty>),
 Column('OriginalAddressID', INTEGER(), ForeignKey('Address.ID'),
        table=<CaseParty>),
 Column('Created', DATETIME(), table=<CaseParty>, nullable=False,
        server_default=DefaultClause(
                <sqlalchemy.sql.elements.TextClause object at 0x74b3569ece10>,
                for_update=False))]
```

The `PartyID` field here can either point to a `Person` or to a `Company`,
depending on the value of the `PartyType` field. Aaargh!

!!! warning
    Tricks like this reduce the referential integrity of the database; there's
    no constraint, for example, that ensures that `PartyID` points to a valid
    object, which forces the front-end to do a lot of work and checks that the
    database back-end could do much more efficiently.

!!! warning
    Note that this "soft" foreign key has also confused SQLAlchemy's
    introspection process -- it didn't find a reason to import the `Company`
    table, so it didn't. (This is also why we had to explicitly include
    `Person` in the introspection process.)

To deal with that, we added a simple "cast" mechanism to the dot-separated
expression parser. We still need to test the type-specifying field to make sure
that the key value will be meaningful, but that's not difficult:

```python
>>> rule = AndRule(
...         SBSYSDBRule("CaseParty.PartyType.Name", "eq", "Person"),
...         SBSYSDBRule(
...                 "CaseParty.Party as Person.Name",
...                  "icontains", "lars"))
```

!!! warning
    This is _another_ reason why you should consider direct database access
    to be a last resort: a fragile database implementation detail has now
    escaped to the outside world.

    If a later change to the system were to replace the "soft" foreign key with
    something more robust -- for example, two new `PersonID` and `CompanyID`
    fields and a database constraint that requires that precisely one of these
    be set -- this `Rule` would break.

### Right-hand references

The SQL translation layer also understands field references when they appear on
the right-hand side of the `SBSYSDBRule` expression, provided that they're
prefixed with an ampersand. For example, we could use the following rule to
efficiently detect cases associated with people who are no longer resident in
the municipality:

```python
>>> rule = AndRule(
...         SBSYSDBRule("CaseParty.PartyType.Name", "eq", "Person"),
...         SBSYSDBRule(
...                 "CaseParty.Party as Person.MunicipalityID",
...                  "neq", "&MunicipalityID"))
```

Of course, the right-hand side of the expression also supports dot-separated
expressions, so we could also have written
`SBSYSDBRule("MunicipalityID", "neq", "&CaseParty.Party as Person.MunicipalityID")`
to get the same effect but with the two sides of the expression flipped.

## Further uses for rules

### More specific scans

OSdatascanner scanner jobs are normally configured to scan organisational units
imported from a directory system of some kind. But SBSYS has its own concept of
users and organisational units, and organisations often don't even bother with
the latter of these. How could we bridge that gap?

Using the components we've already described, this turned out to be very easy:

* collect the OSdatascanner organisational units to be scanned;
* collect all the users from those organisational units;
* collect all the _user principal name_ values from those users, because this
  column is also present in the SBSYS `User` table; and
* build a rule!

```python
>>> ou = OrganizationalUnit.objects.get(name="Educational Services")
>>> users = set(position.account for position in ou.positions.all())
>>> upn_aliases = list(
...         Alias.objects.filter(_alias_type="upn", account__in=users))
>>> user_filter = SBSYSDBRule(
...         "Caseworker.UserPrincipalName", "in", upn_aliases)
```

### Re-impose application-level constraints

If you want OSdatascanner to _voluntarily_ respect the `Case.IsProtected` flag,
or some other security constraint, you can easily write a rule to do that too:

```python
>>> must_not_be_protected = AndRule(
...         SBSYSDBRule("IsProtected", "eq", False),
...         SBSYSDBRule("SecuritySetID", "eq", None))
```

## Reusable bits and pieces

A lot of the more interesting infrastructure we built for SBSYS isn't actually
specific to it:

* the `SBSYSDBRule` class, despite its name, just defines database operations
  (and you can easily add your own -- for example, we added a custom one to
  support organisational unit scanning, `iin`, that performs case-insensitive
  list membership);
* the data source is responsible for opening the database connection in its
  `_generate_source()` method, so you can easily connect to
  [any database supported by SQLAlchemy](https://docs.sqlalchemy.org/en/20/dialects/index.html#dialects),
  not just SQL Server;
* the translation mechanism from OSdatascanner `Rule`s to SQLAlchemy
  `ColumnExpression`s is implemented as a generic `convert_rule_to_select`
  function, where you can specify the SQLAlchemy `Table` the conversion should
  start at; and
* the dot-separated expression parser works in the same way and is also
  implemented as a generic function, `resolve_complex_column_name`.

If you've read this document and you still think direct database access is the
right fit for your data source, consider reusing these components to make the
process easier.
