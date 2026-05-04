# Part of the OSdatascanner system, copyright © 2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from ast import literal_eval
import sys
import yaml
from django.core.management.base import BaseCommand
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import func as sql_func

from os2datascanner.engine2.rules.dummy import AlwaysMatchesRule
from os2datascanner.engine2.rules.logical import AndRule
from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model._staging.sbsysdb_rule import SBSYSDBRule
from os2datascanner.engine2.model._staging.sbsysdb_utilities import (
        exec_expr, convert_rule_to_select, resolve_complex_column_names)
from os2datascanner.projects.admin.adminapp.models.scannerjobs import sbsysdb
from os2datascanner.projects.utils.print_objects import (
        postprocess_object, CollectorActionFactory)


class Command(BaseCommand):
    """Run database query rules against the SQLAlchemy database associated with
    a SBSYS scanner job, and print the results."""

    help = __doc__  # pyright: ignore

    def add_arguments(self, parser):
        parser.add_argument(
            '--filter',
            dest="filt_ops",
            metavar=("LHS", "OP", "RHS"),
            nargs=3,
            type=str,
            action=CollectorActionFactory.make_collector_action("filter"),
            help="a 3-tuple of SBSYSDBRule constructor arguments; RHS will be"
                 " evaluated as a Python literal or as a string if that fails")
        parser.add_argument(
            "--table",
            action="append",
            type=str,
            dest="tables",
            default=[],
            help="replace the SBSYS scanner job's reflection tables; the "
                 " first value given will be used as the base of all queries"
        )
        parser.add_argument(
            "--field",
            action="append",
            type=str,
            dest="fields",
            default=[],
            help="print only the named fields for each row"
        )
        parser.add_argument(
            '--scanner-pk',
            action='store',
            dest="pk",
            required=False,
            type=int,
            help="use a different SBSYS scanner job as a template; by default,"
                 "the most recently-created one is used"
        )
        parser.add_argument(
            '--database',
            action='store',
            dest="database",
            default=None,
            required=False,
            type=str,
            help="use the SBSYS scanner job's server and credentials, but"
                 " connect to a different database (requires --table)",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--limit',
            type=int,
            metavar="COUNT",
            action="store",
            default=10,
            help="the number of results to collect for printing")
        group.add_argument(
            '--no-limit',
            action="store_const",
            const=None,
            dest="limit",
            help="collect all results for printing")

        parser.epilog = (
                """The three arguments to the --filter parameter are passed
                directly to the SBSYSDBRule constructor, so all of the usual
                special operators ("as", "on" and "&") are supported. OP can
                be any of "eq", "neq", "lt", "lte", "gt", "gte", "contains",
                "icontains", "in" or "iin".""")

    def handle(
            self, *args,
            pk, limit, fields, tables, database, filt_ops, **options):
        rule_bits: list[SBSYSDBRule] = []
        for _, lhs, op, rhs in (filt_ops or []):
            try:
                rv = literal_eval(rhs)
            except (ValueError, SyntaxError):
                rv = rhs
            rule_bits.append(SBSYSDBRule(lhs, op, rv))
        # AlwaysMatchesRule doesn't get any special treatment from
        # convert_rule_to_select, but all unrecognised rules reduce to true(),
        # which is what we want if there are no other filters
        rule = AndRule.make(*rule_bits) if rule_bits else AlwaysMatchesRule()

        scanner: sbsysdb.SBSYSDBScanner | None
        if pk is None:
            scanner = sbsysdb.SBSYSDBScanner.objects.order_by("-pk")[0:1].get()
        else:
            scanner = sbsysdb.SBSYSDBScanner.objects.get(pk=pk)

        src, = scanner.generate_sources()

        if database:
            if not tables:
                print("error: option --database requires that at least one"
                      " --table is specified",
                      file=sys.stderr)
                return
            src._db = database
        if tables:
            src._reflect_tables = tuple(tables)
        base_table: str = src.reflect_tables[0]

        with SourceManager() as sm:
            engine, tables, _ = sm.open(src)

            table = tables[base_table]

            (row_count,), = exec_expr(
                    engine, select(sql_func.count("*")).select_from(table))
            print(f" table:        {src._db}.{base_table},"
                  f" {row_count} row(s)")

            constraint, columns = resolve_complex_column_names(
                    table, tables, *fields)
            column_labels = {c.name: c for c in table.columns} | dict(zip(fields, columns))
            s = convert_rule_to_select(
                    rule, table, tables,
                    select().where(*constraint),
                    column_labels)
            if limit is not None:
                s = s.limit(limit)

            all_row_objects = []
            for row in exec_expr(engine, s, *column_labels):
                fixed_dict = {
                    # SQLAlchemy gives us a dict keyed on quoted_name objects,
                    # not plain strings, which confuses yaml.safe_dump. Fix
                    # that up while we do the field inclusion check
                    str(key): value
                    for key, value in row.items()
                    if (not fields) or key in fields
                }
                all_row_objects.append(postprocess_object(fixed_dict))

            print(yaml.safe_dump(all_row_objects, allow_unicode=True))
