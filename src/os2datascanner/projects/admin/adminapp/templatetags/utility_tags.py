# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django import template
from django.utils.translation import gettext_lazy as _, pgettext_lazy

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def _format_unit_compact(iteration, unit_divisor, format_array):
    prefix = " " if iteration > 1 else ""
    return f"{prefix}{unit_divisor} {format_array['abbr']}"


def _format_unit_sentence(iteration, unit_divisor, format_array):
    prefix = " " + _("and") + " " if iteration == 2 else ""
    label = format_array["single"] if unit_divisor == 1 else format_array["multiple"]
    return f"{prefix}{unit_divisor} {label}"


def _build_timespan_parts(seconds, time_formats, style):
    formatted_string = ""
    iteration = 0

    formatter = _format_unit_compact if style == "compact" else _format_unit_sentence

    for unit in time_formats:
        format_array = time_formats[unit]

        # Only proceed if at least one corresponding unit of time is contained in the time span.
        unit_divisor = int(seconds // format_array["seconds"])
        if not unit_divisor:
            continue

        # We only want the two first units which have values greater than zero.
        iteration += 1

        # Grab the remaining seconds.
        seconds = seconds % format_array["seconds"]

        # Add the unit of time to the formatted string.
        formatted_string += formatter(iteration, unit_divisor, format_array)

        if iteration == 2:
            break

    return formatted_string


@register.filter
def format_timespan(seconds, style="sentence"):
    """
    Return a string of the two largest time units of the time span given in seconds.

    style:
      - "sentence": e.g. "1 hour and 23 minutes", "under 1 second"
      - "compact": e.g. "1 h 23 m", "under 1 sec"
    """

    try:
        seconds = float(seconds)
    except ValueError as e:
        print(e)
        return seconds

    if seconds < 1:
        if style == "compact":
            return pgettext_lazy("compact duration", "under 1 sec")
        return _("under 1 second")

    time_formats = {
        "days": {
            "single": _("day"),
            "multiple": _("days"),
            "abbr": pgettext_lazy("abbreviated time unit", "d"),
            "seconds": 60*60*24
        },
        "hours": {
            "single": _("hour"),
            "multiple": _("hours"),
            "abbr": pgettext_lazy("abbreviated time unit", "h"),
            "seconds": 60*60
        },
        "minutes": {
            "single": _("minute"),
            "multiple": _("minutes"),
            "abbr": pgettext_lazy("abbreviated time unit", "min"),
            "seconds": 60
        },
        "seconds": {
            "single": _("second"),
            "multiple": _("seconds"),
            "abbr": pgettext_lazy("abbreviated time unit", "sec"),
            "seconds": 1
        },
    }

    return _build_timespan_parts(seconds, time_formats, style)


@register.filter
def comma_separated_list(qs):
    lst = [acc.username for acc in qs]
    return ", ".join(lst)
