# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.utils.translation import get_language


def get_localised_template_names(template_names):
    """Returns a new list containing language-specific variants of each
    supplied template name. (For example, ["a/b.html"] might return -- for a
    Danish user -- ["a/b.da-dk.html", "a/b.da.html", "a/b.html"]."""
    localised_template_names = []

    languages = []
    active_language = get_language()
    languages.append(active_language)
    if '-' in active_language:
        languages.append(active_language.split("-", maxsplit=1)[0])

    for tn in template_names:
        if '.' in tn:
            head, tail = tn.rsplit(".", maxsplit=1)
            tail = "." + tail
        else:
            head, tail = tn, ""
        for code in languages:
            localised_template_names.append(head + f".{code}" + tail)
        localised_template_names.append(tn)
    return localised_template_names
