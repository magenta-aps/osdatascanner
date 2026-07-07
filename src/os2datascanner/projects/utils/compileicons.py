# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

# XXX: The true (project-relative) path of this file is src/os2datascanner/
# projects/utils/compileicons.py; the administration system references it via
# a relative symbolic link. Don't edit it through the symbolic link, as that
# might break it!
#
# Unlike makemessages/compilemessages, this command is intentionally *not*
# symlinked into the report module: the icon font is one genuinely shared
# asset, not per-app content, so it should only be runnable from one place.
# `admin` was chosen to match the existing convention for the other
# truly-shared apps (grants, shared, core_organizational_structure) in
# docs/development_environment/translations.md, which always exec into
# `admin` rather than `report`.

import json
import re
from pathlib import Path

import requests
from django.core.management.base import BaseCommand, CommandError

from os2datascanner.engine2.factory import make_webretrier

FONT_DIR = Path(__file__).resolve().parent.parent / "static" / "fonts" / "materialsymbols"
MANIFEST_PATH = FONT_DIR / "icons.json"
OUTPUT_PATH = FONT_DIR / "MaterialSymbols-Outlined.woff2"

# A modern desktop UA is required to get a woff2 response from the CSS2 API.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


class Command(BaseCommand):

    help = (
        "Regenerate the self-hosted Material Symbols subset font from "
        "static/fonts/materialsymbols/icons.json, using Google's icon-name "
        "and axis-instancing subsetting "
        "(see https://developers.google.com/fonts/docs/material_symbols). "
        "Run this after adding a new icon, or a new font-variation-settings "
        "value, to that file."
    )

    def handle(self, *args, **options):
        manifest = json.loads(MANIFEST_PATH.read_text())
        icon_names = ",".join(sorted(manifest["icons"]))

        axes = {key: value for key, value in manifest["axes"].items() if key != "//"}
        axis_names = ",".join(axes.keys())
        axis_ranges = ",".join(f"{lo}..{hi}" for lo, hi in axes.values())

        css_url = (
            "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:"
            f"{axis_names}@{axis_ranges}&icon_names={icon_names}&display=block"
        )

        retrier = make_webretrier()

        self.stdout.write(f"Fetching subset definition for {len(manifest['icons'])} icons...")
        css_response = retrier.run(
            requests.get, css_url, headers={"User-Agent": USER_AGENT}, timeout=30)
        css_response.raise_for_status()

        matches = re.findall(r"src: url\(([^)]+)\) format\('woff2'\)", css_response.text)
        if len(matches) != 1:
            raise CommandError(
                f"Expected exactly one woff2 URL in the response, found {len(matches)}:\n"
                f"{css_response.text}")

        font_url = matches[0]
        self.stdout.write(f"Downloading subset font from {font_url}...")
        font_response = retrier.run(requests.get, font_url, timeout=30)
        font_response.raise_for_status()

        OUTPUT_PATH.write_bytes(font_response.content)

        size_kb = len(font_response.content) / 1024
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH} ({size_kb:.1f} KB, {len(manifest['icons'])} icons)."))
