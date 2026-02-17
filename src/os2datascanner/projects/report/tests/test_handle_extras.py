# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from ..reportapp.templatetags.handle_extras import find_svg_icon


class TestHandleExtra:

    @pytest.mark.parametrize('type_label,expected', [
        ('web', "components/svg-icons/icon-web.svg"),
        ('smbc', "components/svg-icons/icon-smbc.svg"),
        ('msgraph-mail',
         "components/svg-icons/icon-msgraph-mail.svg"),
        ('googledrive', "components/svg-icons/icon-googledrive.svg"),
        ('gmail', "components/svg-icons/icon-gmail.svg"),
        ('dropbox', "components/svg-icons/icon-dropbox.svg"),
        ('sbsys', "components/svg-icons/icon-default.svg"),
        ('ews', "components/svg-icons/icon-ews.svg"),
    ])
    def test_find_svg_icon(self, type_label, expected):
        assert find_svg_icon(type_label=type_label) == expected
