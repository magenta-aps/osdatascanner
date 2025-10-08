"""Prints YAML or JSON summaries of Django database objects."""

# XXX: The true (project-relative) path of this file is src/os2datascanner/
# projects/utils/print_objects.py; the administration system and report module
# reference it by relative symbolic links. Don't edit it through the symbolic
# links, as that might break them!

from ast import literal_eval
import sys
import json
import uuid
import yaml
from pprint import pformat
import datetime
from functools import partial

import argparse
from django.apps import apps
from django.db import models
from django.db.models.query import QuerySet
from django.core.exceptions import FieldError
from django.core.management.base import BaseCommand
import recurrence


model_mapping = {model.__name__: model for model in apps.get_models()}


eprint = partial(print, file=sys.stderr)


def get_full_typename(t: type) -> str:
    return f"{t.__module__}.{t.__qualname__}"


def separate(it, criterion) -> list:
    """Reorders the given iterable to put all the elements for which the
    criterion function returns True at the start of the list. (The order is
    otherwise not changed.)"""
    left = []
    right = []
    for k in it:
        if criterion(k):
            left.append(k)
        else:
            right.append(k)
    return left + right


def model_class(model: str) -> type:
    """Returns a named Django model class.

    Classes defined in the OSdatascanner code base are preferred over others.
    To force a model to be selected from a particular app, prefix the name with
    its label (for example, "recurrence.Rule")."""
    match model.split(".", maxsplit=1):
        case [simple_name]:
            app_label = None
            model_name = simple_name
        case [app_label, simple_name]:
            app_label = app_label
            model_name = simple_name

    for mclass in separate(apps.get_models(),
                           lambda t: "os2datascanner" in t.__module__):
        if mclass.__name__ != model_name:
            continue

        match (app_label, mclass._meta.app_label):
            case (None, _):
                return mclass
            case (p, q) if p == q:
                return mclass
    else:
        raise argparse.ArgumentTypeError(
                "'{0}': Model class not known".format(model))


def parse_fl_string(flt):
    """Transforms a string representing a Django filter expression (for
    example, ['scanner__pk=20', 'owner__username__icontains="af@"']) into a
    dict that can be used as keyword arguments to a function requiring a field
    lookup.

    The right hand side of the expression can have several forms:

    * "F:" followed by an expression will become a Django F() object;
    * "Count:" followed by an expression will become a Django Count() object;
    * a Python literal will be parsed (as though by ast.literal_eval) to an
      appropriately typed value; and
    * anything else will be treated as a string literal."""
    lhs, rhs = flt.split("=", maxsplit=1)
    try:
        rhs = literal_eval(rhs)
    except (ValueError, SyntaxError,):
        if ":" in rhs:
            match rhs.split(":", maxsplit=1):
                case ("Count", field_expr):
                    rhs = models.Count(field_expr)
                case ("F", field_expr):
                    rhs = models.F(field_expr)
                case _:
                    # Do nothing; just leave rhs as a string
                    pass
        else:
            # Do nothing; just leave rhs as a string
            pass
    return lhs, rhs


def build_queryset_from(
        model: type,
        filt_ops: list[list[str]]) -> QuerySet:
    manager = model.objects
    model_name = model._meta.object_name
    model_app = model._meta.app_label

    if hasattr(manager, "select_subclasses"):
        queryset = manager.select_subclasses().all()
    else:
        queryset = manager.all()

    print(f" table:        {model_app}.{model_name},"
          f" {queryset.count()} row(s)")

    for verb, fexpr, *rest in (filt_ops or ()):
        lhs, rhs = parse_fl_string(fexpr)
        try:
            match (verb, *rest):
                case ("filter",):
                    queryset = queryset.filter(**{lhs: rhs})
                case ("exclude",):
                    queryset = queryset.exclude(**{lhs: rhs})
                case ("annotate",):
                    queryset = queryset.annotate(**{lhs: rhs})
                case ("alias",):
                    queryset = queryset.alias(**{lhs: rhs})
                case _:
                    raise ValueError(
                            "BUG: didn't understand the verb"
                            f" {verb}")
        except FieldError:
            eprint(
                    f"""Django didn't like the field lookup "{lhs}"."""
                    " Valid fields at this point are:")
            for field in get_possible_fields(queryset):
                eprint(f"\t{field}")
            sys.exit(2)

    if filt_ops:
        print(f" after filter: {queryset.count()} row(s)")

    return queryset


class CollectorActionFactory:
    class Action(argparse.Action):
        def __init__(self, *args, prefix, **kwargs):
            super().__init__(*args, **kwargs)
            self.prefix = list(prefix)

        def __call__(self, parser, namespace, values, option_string):
            if getattr(namespace, self.dest, None) is None:
                setattr(namespace, self.dest, [])
            if not isinstance(values, (list, tuple,)):
                values = [values]
            getattr(namespace, self.dest).append(self.prefix + values)

    def make_collector_action(self, *prefix):
        return partial(
                CollectorActionFactory.Action,
                prefix=prefix)


def get_possible_fields(qs: QuerySet) -> list[str]:
    """Returns all of the fields, including annotations, available in the given
    QuerySet."""
    # Trivially adapted from django.db.models.sql.query.Query.names_to_path
    return sorted([
            *models.sql.query.get_field_names_from_opts(qs.model._meta),
            *qs.query.annotation_select,
            *qs.query._filtered_relations])


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        caf = CollectorActionFactory()

        parser.add_argument(
            '--exclude',
            dest="filt_ops",
            metavar="FL",
            type=str,
            action=caf.make_collector_action("exclude"),
            help="a Django field lookup to exclude objects")
        parser.add_argument(
            '--filter',
            dest="filt_ops",
            metavar="FL",
            type=str,
            action=caf.make_collector_action("filter"),
            help="a Django field lookup to filter objects")
        parser.add_argument(
            '--annotate',
            dest="filt_ops",
            metavar="FL",
            type=str,
            action=caf.make_collector_action("annotate"),
            help="a Django field lookup describing an annotation to add to the"
                 " query set")
        parser.add_argument(
            '--alias',
            dest="filt_ops",
            metavar="FL",
            type=str,
            action=caf.make_collector_action("alias"),
            help="a Django field lookup describing an alias to add to the"
                 " query set")

        parser.add_argument(
            '--field',
            dest="fields",
            metavar="NAME",
            type=str,
            action="append",
            help="a Django field name to include in the output (can be used"
                 " multiple times; if not used, all fields are included)")
        parser.add_argument(
            '--distinct',
            action="store_true",
            help="generate a final query with SELECT DISTINCT"
                 " (use with --order-by)")

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--order-by',
            type=str,
            metavar="EXPR",
            action="store",
            help="the Django field (expression) to order the results by"
                 " (ascending)")
        group.add_argument(
            '--order-by-desc',
            type=str,
            metavar="EXPR",
            action="store",
            default="pk",
            help="the Django field (expression) to order the results by"
                 " (descending)")

        parser.add_argument(
            '--offset',
            type=int,
            action="store",
            default=None,
            help="the offset at which to start to collect results")
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

        parser.add_argument(
            '--with-sql',
            action="store_true",
            help="also print the computed SQL statement for the query")
        parser.add_argument(
            '--json',
            dest="format",
            action="store_const",
            const="json",
            default="yaml",
            help="output results as JSON, not YAML")
        parser.add_argument(
            '--pprint',
            dest="format",
            action="store_const",
            const="pprint",
            help="output raw QuerySets using Python's pretty-printer")
        parser.add_argument(
            '--no-results',
            dest="format",
            action="store_const",
            const=None,
            help="don't actually print the final computed results")
        parser.add_argument(
            'model',
            type=model_class,
            help='a Django model class',
        )

        parser.epilog = (
                """Simple Django field lookups with a Python literal
                ('scanner_pk=20', 'account__username__icontains="af@"')
                are supported, but for convenience you can also omit quotation
                marks around string values ("name__icontains=bestyrelse") or
                use a special colon-separated prefix to invoke a Django
                aggregation or query function
                ("match_count=Count:reports",
                "username=F:account__username").')""")

    def handle(  # noqa CCR001
            self, *,
            order_by, order_by_desc, limit, offset, model, fields,
            filt_ops, with_sql, format, distinct, **kwargs):
        queryset = build_queryset_from(model, (filt_ops or []))

        queryset = queryset.order_by(
                order_by
                if order_by is not None
                else f"-{order_by_desc}")
        if distinct:
            queryset = queryset.distinct()

        use_values = format in ("json", "yaml")

        if use_values:
            queryset = queryset.values(*(fields or []))

        if (limit, offset) != (None, None):
            off = offset or 0
            lim = max(1, limit or 0)
            qslice = slice(off, off + lim)
            queryset = queryset[qslice]
            print(f" after slice:  {queryset.count()} row(s) (offset {off})")

        if with_sql:
            print(queryset.query)

        if format is None:
            return

        queryset = list(queryset)
        if use_values:
            # Lightly postprocess the results: obscure passwords and prevent
            # UUIDField objects from being dumped in their unhelpful raw form
            for obj in queryset:
                for key, value in obj.items():
                    key_is_suspicious = (
                            "password" in key
                            or "secret" in key
                            or "token" in key)
                    if key_is_suspicious and isinstance(value, str):
                        obj[key] = "█" * min(len(value), 8)
                    elif isinstance(
                            value,
                            (uuid.UUID, datetime.date, datetime.datetime,
                             recurrence.Recurrence,)):
                        # Types for which we trust str() (with a tag)
                        type_name = get_full_typename(type(value))
                        obj[key] = f"{value!s} [{type_name}]"
                    elif not isinstance(
                            value,
                            (int, float, dict, str, list, type(None))):
                        obj[key] = {
                            "unserialisable": True,
                            "module": (type_here := type(value)).__module__,
                            "qualname": type_here.__qualname__,
                            "str": str(value),
                            "repr": repr(value),
                        }

        match format:
            case "json":
                representation = json.dumps(
                        queryset, ensure_ascii=False, default=repr,
                        indent=True)
            case "yaml":
                representation = yaml.safe_dump(
                        queryset, allow_unicode=True)
            case "pprint":
                representation = pformat(queryset)

        print(representation.rstrip())
