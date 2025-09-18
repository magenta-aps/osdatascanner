#!/usr/bin/env python

"""Summarises an OS2datascanner data source, showing the system's view of
it."""

from sys import stderr
import signal
import argparse
import structlog
import traceback

from os2datascanner.utils.log_levels import log_levels
from os2datascanner.engine2 import settings as engine2_settings
from os2datascanner.engine2.model.core import Source, SourceManager
from os2datascanner.engine2.model.core import FileResource
from os2datascanner.engine2.model.core import UnknownSchemeError
from .utils import DemoSourceUtility


def do_nothing(*args, **kwargs):
    pass


printfunc = print


def format_d(depth, fmt, *args, **kwargs):
    return "{0}{1}".format("  " * depth, fmt.format(*args, **kwargs))


def print_source(  # noqa
        manager, *source_path,
        guess=False, summarise=False, metadata=False, max_depth=None,
        hints=False, censor=True):  # noqa
    base_source = source_path[0]

    source = source_path[-1]
    depth = len(source_path)
    try:
        for handle in source.handles(manager):
            disp_handle = handle.censor() if censor else handle
            printfunc(format_d(depth, "{0}", disp_handle))
            if hints:
                for k, v in (disp_handle._hints or {}).items():
                    printfunc(format_d(depth + 1, "hint:{0} {1}", k, v))

                # These are hints of sorts, but aren't stored in _hints
                printfunc(format_d(
                        depth + 1, "hint:referrer {0}", disp_handle.referrer))
                if p_url := disp_handle.presentation_url:
                    printfunc(format_d(
                            depth + 1, "hint:presentation_url {0}", p_url))

            if handle not in base_source:
                printfunc(format_d(depth + 1, "(foreign Handle)"))
                continue

            if summarise:
                resource = handle.follow(manager)
                try:
                    if isinstance(resource, FileResource):
                        size = resource.get_size()
                        mime = (resource.compute_type()
                                if not guess else handle.guess_type())
                        lm = resource.get_last_modified()
                        printfunc(format_d(depth + 1, "size {0} bytes", size))
                        printfunc(format_d(depth + 1, "type {0}", mime))
                        printfunc(format_d(depth + 1, "lmod {0}", lm))
                except Exception:
                    printfunc(format_d(depth + 1, "not available"))
            if metadata:
                resource = handle.follow(manager)
                for k, v in resource.get_metadata().items():
                    printfunc(format_d(depth + 1, "metadata:{0} {1}", k, v))
            if max_depth is None or depth < max_depth:
                derived_source = Source.from_handle(
                        handle, manager if not guess else None)
                if derived_source:
                    print_source(
                            manager, *source_path, derived_source,
                            guess=guess, summarise=summarise,
                            metadata=metadata, max_depth=max_depth,
                            hints=hints, censor=censor)
    except Exception:
        print(
                format_d(depth, f"{type(source).__name__}: unexpected error:"),
                file=stderr)
        lines = traceback.format_exc().strip().split("\n")
        for line in lines:
            print(format_d(depth + 1, "{0}", line), file=stderr)


def add_control_arguments(parser):
    parser.add_argument(
            "--guess-mime",
            action='store_true',
            dest='guess',
            help='Compute the MIME type of each file'
                 ' based on its filename. (default)',
            default=True)
    parser.add_argument(
            "--compute-mime",
            action='store_false',
            dest='guess',
            help='Compute the MIME type of each file based on its content.')
    parser.add_argument(
            "--summarise",
            action='store_true',
            dest='summarise',
            help='Print a brief summary of the content of each file.')
    parser.add_argument(
            "--metadata",
            action='store_true',
            dest='metadata',
            help='Print the metadata associated with each file.')
    parser.add_argument(
            "--max-depth",
            metavar="DEPTH",
            type=int,
            help="Don't recurse deeper than %(metavar)s levels.")
    parser.add_argument(
            "--hints",
            action="store_true",
            help="Print the hints associated with each file.")
    parser.add_argument(
            "--no-censor",
            dest="censor",
            action="store_false",
            help="Don't censor handles before printing them.")
    parser.add_argument(
            "--setting",
            metavar=("KEY", "VALUE"),
            nargs=2,
            action="append",
            dest="settings",
            default=[],
            help="Override an engine2 setting for the duration of this scan.")
    parser.add_argument(
            "--stop",
            action="store_true",
            help="Raise the SIGSTOP signal after exploring each source.")
    parser.add_argument(
            "-q", "--quiet",
            action="store_true",
            help="Explore sources without printing anything (apart from"
                 " errors) to the console.")


def add_arguments(parser):
    parser.add_argument(
            "urls",
            metavar="URL",
            help="A URL to be explored, for example file:///usr/share/doc or"
                 " https://www.magenta.dk. (Note that not all OS2datascanner"
                 " sources have URL representations.)",
            nargs='+')
    add_control_arguments(parser)
    # Do note that this isn't our _usual_ way of setting log level. You are also able to do so
    # through environment variables - but it makes sense to be able to provide it as an argument
    # here, because we're not interested in running a new container for this command.
    parser.add_argument(
            "--log-level",
            default="info",
            help="Set the logging level.",
            choices=log_levels.keys(),
        )


def main():  # noqa: C901, CCR001
    parser = argparse.ArgumentParser()
    add_arguments(parser)

    args = parser.parse_args()

    if args.quiet:
        global printfunc
        printfunc = do_nothing

    # Patch the settings module
    for key, value in args.settings:
        try:
            value = float(value)
            if value.is_integer():
                value = int(value)
        except ValueError:
            pass

        # Work out where in the settings hierarchy to apply this patch. This
        # code is a bit fiddly because the first tier of the hierarchy is
        # fields in a module, and then everything after that is a dict...
        components = key.split(".")
        here = engine2_settings
        while here and (head := components[0]) and (tail := components[1:]):
            try:
                here = here[head]
            except TypeError:  # here isn't a dict; use getattr
                here = getattr(here, head, None)
            components = tail

        if here is None:
            continue

        try:
            if head in here:
                here[head] = value
        except TypeError:
            if hasattr(here, head):
                setattr(here, head, value)

    # Set level for root logger
    structlog.get_logger("os2datascanner").setLevel(log_levels[args.log_level])

    with SourceManager() as sm:
        for i in args.urls:
            try:
                s = DemoSourceUtility.from_url(i)
                if not s:
                    print("{0}: URL parsing failure".format(i), file=stderr)
                else:
                    print_source(
                            sm, s,
                            guess=args.guess,
                            summarise=args.summarise,
                            metadata=args.metadata,
                            max_depth=args.max_depth,
                            hints=args.hints,
                            censor=args.censor)
                    if args.stop:
                        signal.raise_signal(signal.SIGSTOP)
            except UnknownSchemeError:
                print("{0}: unknown URL scheme".format(i), file=stderr)


if __name__ == '__main__':
    main()
