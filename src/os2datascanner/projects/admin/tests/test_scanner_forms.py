# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from os2datascanner.projects.shared.forms import GroupingModelForm
from os2datascanner.projects.admin.adminapp.forms.shared import ScanMaxFileSizeWidget


class TestBuildItems:
    """GroupingModelForm._build_items silently skips fields absent from field_dict."""

    @pytest.fixture
    def form(self):
        # Bypass ModelForm.__init__ — we only need the method, not a bound model.
        return GroupingModelForm.__new__(GroupingModelForm)

    def test_present_field_is_included(self, form):
        result = form._build_items(["field_a"], {"field_a": ("bf", "")})
        assert len(result) == 1
        assert result[0] == {"type": "field", "bf": "bf", "errors": ""}

    def test_missing_field_is_skipped(self, form):
        result = form._build_items(["missing"], {})
        assert result == []

    def test_only_present_fields_appear_in_mixed_spec(self, form):
        field_dict = {"present": ("bf", "")}
        result = form._build_items(["present", "missing"], field_dict)
        assert len(result) == 1
        assert result[0]["bf"] == "bf"

    def test_subgroup_skips_missing_fields(self, form):
        field_dict = {"present": ("bf", "")}
        spec = [("Sub heading", ["present", "missing"])]
        result = form._build_items(spec, field_dict)
        assert len(result) == 1
        assert result[0]["type"] == "group"
        assert len(result[0]["items"]) == 1
        assert result[0]["items"][0]["bf"] == "bf"

    def test_empty_subgroup_after_all_fields_removed(self, form):
        spec = [("Empty sub", ["gone_a", "gone_b"])]
        result = form._build_items(spec, {})
        assert result[0]["type"] == "group"
        assert result[0]["items"] == []


class TestScanMaxFileSizeWidget:
    """ScanMaxFileSizeWidget.get_context produces a checked/unchecked toggle."""

    @pytest.fixture
    def widget(self):
        return ScanMaxFileSizeWidget()

    def _toggle_checked(self, widget, value):
        ctx = widget.get_context("max_pdf_size", value, {})
        return ctx["toggle"]["attrs"].get("checked", False)

    def test_none_is_unchecked(self, widget):
        assert not self._toggle_checked(widget, None)

    def test_zero_int_is_unchecked(self, widget):
        assert not self._toggle_checked(widget, 0)

    def test_zero_string_is_unchecked(self, widget):
        assert not self._toggle_checked(widget, "0")

    def test_positive_int_is_checked(self, widget):
        assert self._toggle_checked(widget, 10) is True

    def test_negative_int_is_checked(self, widget):
        # The widget has no knowledge of min_value=0 on the field; negative
        # values are truthy and therefore render as checked.
        assert self._toggle_checked(widget, -1) is True

    def test_checkbox_label_is_passed_through(self, widget):
        widget.checkbox_label = "Limit PDF size"
        ctx = widget.get_context("max_pdf_size", 5, {})
        assert ctx["checkbox_label"] == "Limit PDF size"
