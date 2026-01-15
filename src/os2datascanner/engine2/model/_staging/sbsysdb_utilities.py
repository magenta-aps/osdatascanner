import structlog

from sqlalchemy import (
        and_, or_, not_, true, false,
        Table, Column)
from sqlalchemy.sql.elements import BinaryExpression, OperatorExpression
from sqlalchemy.sql.expression import Select

from os2datascanner.utils.ref import Counter
from os2datascanner.engine2.rules import logical
from os2datascanner.engine2.rules.rule import Rule

from .sbsysdb_rule import SBSYSDBRule


logger = structlog.get_logger("engine2")


__undefined = object()


def get_first_attr(obj: object, *attrs: str, default=__undefined):
    """Returns the first of the named attributes present on the given object.
    Raises AttributeError if none of the attributes are present and no default
    value is provided."""
    while attrs:
        attr, *attrs = attrs
        try:
            return getattr(obj, attr)
        except AttributeError:
            if not attrs:
                if default is not __undefined:
                    return default
                raise


def resolve_complex_column_name(
        start: Table, col_name: str, all_tables) -> (Select, Column):
    """Given a Table at which to start and a complex column name that may
    traverse several tables (for example,
    "Creator.ContactInfo.Address.Postcode"), returns the conjunction of all the
    extra constraints required by the traversal and a reference to the column
    that was eventually selected.

    The traversal logic can follow foreign key relations automatically, but
    it also supports two syntactic variants:

    - "Field as TableName" for pseudo-foreign keys:
      "Subject as Person.Address", "Subject as Company.RegisteredAddress",
      "Subject as Animal.Owner as Person.Address" etc.; and
    - "Field as ThroughTable on CaseID" for through tables, where you need to
      select on something that /isn't/ the other table's primary key."""
    here = start
    *field_path, last = col_name.split(".")

    # Worked example: starting at Sag and trying to get to
    # Behandler.Adresse.Landekode...

    links = []

    for part in field_path:
        column = None
        explicit_cast = None
        other_table_key = None

        match part.split():
            case [name]:
                column = name
            case [name, "as", table]:
                # Some SBSYS columns are "soft" foreign keys: the value of
                # another field governs what they point at (groan). To support
                # that, we allow the points-to relation to be set explicitly
                column = name
                explicit_cast = table
            case [name, "as", table, "on", otherkey]:
                # Sometimes we have through tables (double groan), so we need
                # to target something other than the primary key when we select
                # from another table
                column = name
                explicit_cast = table
                other_table_key = otherkey
            case [name, "on", otherkey]:
                column = name
                other_table_key = name
            case _:
                raise SyntaxError(part)

        # ... we first select the "BehandlerID" (or "Behandler") column...
        link_column = get_first_attr(here.c, column + "ID", column)

        if not explicit_cast:
            # ... then we follow the foreign key to get a reference to the
            # Bruger table on the other side...
            fk, = link_column.foreign_keys
            other_table = fk.column.table
        else:
            other_table = all_tables[explicit_cast]

        # ... then we (implicitly) join the Bruger table into our query...
        if not other_table_key:
            other_table_pk, = other_table.primary_key
        else:
            other_table_pk = get_first_attr(
                    other_table.c, other_table_key + "ID", other_table_key)
        links.append(link_column == other_table_pk)
        # ... and continue following the chain at Bruger, where we do the
        # same trick again for "Adresse" -> AdresseID -> <table Adresse>
        here = other_table

    # Finally, we take the last part of the column name ("Landekode") and look
    # it up in the table we've ended up at
    # (here we assume that the "-ID" suffix is less likely to occur, but it's
    # still allowed)
    last_column = get_first_attr(here.c, last, last + "ID")

    return links, last_column


def resolve_complex_column_names(
        start: Table, all_tables, *col_names: str):
    """Resolves multiple complex column names at once as though by
    resolve_complex_column_name, returning a single unified constraint object
    and a list of the resolved columns."""
    constraint = []
    columns = []
    for name in col_names:
        c, r = resolve_complex_column_name(start, name, all_tables)
        constraint.extend(c)
        columns.append(r)
    return constraint, columns


def _rule_lhs_to_cv(
        lhs,
        table, all_tables,
        virtual_columns):
    # The left-hand side of a SBSYSDBRule expression can be one of two
    # things: either a virtual column or a (perhaps complex) column name. Work
    # out which it is
    lhs_constraints = []
    if virtual_columns and lhs in virtual_columns:
        lhs_val = virtual_columns.get(lhs)
    else:
        lhs_constraints, lhs_val = resolve_complex_column_name(
                table, lhs, all_tables)

    return lhs, lhs_constraints, lhs_val


def _rule_rhs_to_cv(
        rhs,
        table, all_tables):
    # The right-hand side of a SBSYSDBRule expression is either a normal value
    # or (if it's a string starting with "&") a reference to another column
    rhs_constraints = []
    match rhs:
        case str() if rhs.startswith("&"):
            rhs = rhs[1:]
            rhs_constraints, rhs_val = resolve_complex_column_name(
                    table, rhs, all_tables)
        case str() if rhs.startswith("\\"):
            rhs = rhs_val = rhs[1:]
        case _:
            rhs_val = rhs

    return rhs, rhs_constraints, rhs_val


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

    def rule_to_constraints(r) -> (list[BinaryExpression], OperatorExpression):
        """Recursively converts an OSdatascanner Rule into a SQLAlchemy
        constraint.

        This function updates the column_labels dictionary with each new column
        required by the expression, labelled with its name from the Rule; this
        information will eventually be required to turn the constraint into a
        complete Select expression."""
        match r:
            case logical.AndRule() | logical.OrRule():
                joins = []
                exprs = []
                for c in r.components:
                    join, expr = rule_to_constraints(c)
                    joins.extend(join)
                    exprs.append(expr)

                return joins, (and_(true(), *exprs)
                               if isinstance(r, logical.AndRule)
                               else or_(false(), *exprs))

            case logical.NotRule():
                join, expr = rule_to_constraints(r._rule)
                return join, not_(expr)

            case SBSYSDBRule(lhs, op, rhs):
                lhs_cn, lhs_constraints, lhs_val = _rule_lhs_to_cv(
                        lhs, table, all_tables, virtual_columns)
                rhs_cn, rhs_constraints, rhs_val = _rule_rhs_to_cv(
                        rhs, table, all_tables)

                if lhs_cn not in column_labels:
                    column_labels[lhs_cn] = lhs_val
                if isinstance(rhs_val, Column) and rhs_cn not in column_labels:
                    column_labels[rhs_cn] = rhs_val

                return (lhs_constraints + rhs_constraints,
                        op.func_db(lhs_val, rhs_val))

            case _:
                # For now, we assume that any other OSdatascanner rule plays no
                # part in the SQL query
                return [], true()

    join, expr = rule_to_constraints(rule)
    # To turn our constraint object into a valid Select expression, we need to
    # make sure we actually select the columns required by the constraints.
    # Luckily rule_to_constraints stashes those away in the column_labels dict
    rv = initial_select.add_columns(*column_labels.values())
    return rv.where(*join, expr)


def exec_expr(
        engine, expr: Select, *labels: str, rows: Counter | None = None):
    with engine.connect() as connection, connection.begin():
        logger.debug(
                "executing SBSYS database query",
                query=str(expr), params=expr.compile().params)

        # Simulate Django's iterator() (with its default page size of 2000)
        # to avoid allocating too much memory
        for db_row in connection.execute(
                expr, execution_options={
                    "yield_per": 2000
                }):
            yield dict(zip(labels, db_row)) if labels else tuple(db_row)
            Counter.try_incr(rows)
