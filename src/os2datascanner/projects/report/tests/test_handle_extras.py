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
