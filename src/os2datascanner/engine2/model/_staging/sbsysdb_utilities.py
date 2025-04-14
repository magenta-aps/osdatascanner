import structlog

from sqlalchemy import (
        and_, or_, not_, true, false,
        Table, Column)
from sqlalchemy.sql.expression import Select

from os2datascanner.engine2.rules import logical
from os2datascanner.engine2.rules.rule import Rule

from .sbsysdb_rule import SBSYSDBRule


logger = structlog.get_logger("engine2")


def resolve_complex_column_name(
        start: Table, col_name: str, all_tables) -> (Select, Column):
    """Given a Table at which to start and a complex column name that may
    traverse several tables (for example,
    "Creator.ContactInfo.Address.Postcode"), returns the conjunction of all the
    extra constraints required by the traversal and a reference to the column
    that was eventually selected.

    The traversal logic can follow foreign key relations automatically, but
    it also supports a cast syntax ("Field as TableName") for pseudo-foreign
    keys: "Subject as Person.Address", "Subject as Company.RegisteredAddress",
    "Subject as Animal.Owner as Person.Address" etc."""
    here = start
    *field_path, last = col_name.split(".")

    # Worked example: starting at Sag and trying to get to
    # Behandler.Adresse.Landekode...

    links = []

    for part in field_path:
        explicit_cast = None
        if " as " in part:
            # Some SBSYS columns are "soft" foreign keys: the value of another
            # field governs what they point at (groan). To support that, we
            # allow the points-to relation to be set explicitly
            part, explicit_cast = part.split(" as ", maxsplit=1)

        # ... we first select the "BehandlerID" column...
        try:
            link_column = getattr(here.c, part + "ID")
        except AttributeError:
            # Handle foreign key reference columns that don't use the "ID"
            # name suffix convention
            link_column = getattr(here.c, part)

        if not explicit_cast:
            # ... then we follow the foreign key to get a reference to the
            # Bruger table on the other side...
            fk, = link_column.foreign_keys
            other_table = fk.column.table
        else:
            other_table = all_tables[explicit_cast]

        # ... then we (implicitly) join the Bruger table into our query...
        other_table_pk, = other_table.primary_key
        links.append(link_column == other_table_pk)
        # ... and continue following the chain at Bruger, where we do the
        # same trick again for "Adresse" -> AdresseID -> <table Adresse>
        here = other_table

    # Finally, we take the last part of the column name ("Landekode") and look
    # it up in the table we've ended up at
    return and_(*links), getattr(here.c, last)


def resolve_complex_column_names(
        start: Table, all_tables, *col_names: str):
    """Resolves multiple complex column names at once as though by
    resolve_complex_column_name, returning a single unified constraint object
    and a list of the resolved columns."""
    constraint = true()
    columns = []
    for name in col_names:
        c, r = resolve_complex_column_name(start, name, all_tables)
        constraint = and_(constraint, c)
        columns.append(r)
    return constraint, columns


def convert_rule_to_select(
        rule: Rule,
        table: Table, all_tables,
        initial_select: Select, column_labels: dict[str, Column],
        virtual_columns: dict[str, object] = None) -> Select:
    """Converts an OSdatascanner Rule containing SBSYSDBRule objects into a
    corresponding SQLAlchemy Select expression.

    The resulting expression is guaranteed to select columns in the same order
    as the keys of the column_labels dict. (One useful consequence of this is
    that you can make a mapping from field names to results by just zipping
    the keys together with a result tuple.)"""

    def rule_to_constraints(r):
        """Recursively converts an OSdatascanner Rule into a SQLAlchemy
        constraint.

        This function updates the column_labels dictionary with each new column
        required by the expression, labelled with its name from the Rule; this
        information will eventually be required to turn the constraint into a
        complete Select expression."""
        match r:
            case logical.AndRule():
                return and_(
                        true(),
                        *(rule_to_constraints(c) for c in r.components))

            case logical.OrRule():
                return or_(
                        false(),
                        *(rule_to_constraints(c) for c in r.components))

            case logical.NotRule():
                return not_(rule_to_constraints(r._rule))

            case SBSYSDBRule(field_name, op, value) \
                    if virtual_columns and field_name in virtual_columns:
                virtual_column = virtual_columns.get(field_name)
                if field_name not in column_labels:
                    column_labels[field_name] = virtual_column
                return op.func_db(virtual_column, value)

            case SBSYSDBRule(field_name, op, value):
                extra_constraints, column = resolve_complex_column_name(
                        table, field_name, all_tables)
                if field_name not in column_labels:
                    column_labels[field_name] = column
                return and_(extra_constraints, op.func_db(column, value))

            case _:
                # For now, we assume that any other OSdatascanner rule plays no
                # part in the SQL query
                return true()

    constraints = rule_to_constraints(rule) if rule else true()
    # To turn our constraint object into a valid Select expression, we need to
    # make sure we actually select the columns required by the constraints.
    # Luckily rule_to_constraints stashes those away in the column_labels dict
    return initial_select.add_columns(
            *column_labels.values()).where(constraints)


def exec_expr(engine, expr: Select, *labels: str):
    with engine.begin() as connection:
        logger.debug(
                "executing SBSYS database query",
                query=str(expr), params=expr.compile().params)

        # Simulate Django's iterator() (with its default page size of 2000)
        # to avoid allocating too much memory
        for db_row in connection.execute(
                expr, execution_options={
                    "yield_per": 2000
                }):
            yield dict(zip(labels, db_row))
