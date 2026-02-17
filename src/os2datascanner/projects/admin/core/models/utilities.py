# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from enum import Flag, Enum

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def _new_obj_with_value_and_label(cls, value, label):
    obj = object.__new__(cls)
    obj._value_ = value
    obj.label = label
    return obj


def _get_choices(cls):
    return [(f.value, f.label[0].upper()+f.label[1:]) for f in cls]


class ModelChoiceEnum(Enum):
    """Base class for Enums used as choices for model fields."""

    def __new__(cls, value, label):
        return _new_obj_with_value_and_label(cls, value, label)

    @classmethod
    def choices(cls):
        return _get_choices(cls)


# It's possible this could be implemented using a custom model field instead
class ModelChoiceFlag(Flag):
    """Base class for Flags used as choices for model fields.

    Implements utility functions to ease use of flags for model field values.
    New members are defined by a (value, label) tuple to support translation
    of choice labels.
    """

    def __new__(cls, value, label):
        """Takes an integer value and a label, returns new flag member."""
        return _new_obj_with_value_and_label(cls, value, label)

    @classmethod
    def choices(cls):
        """Return list of flags formatted as choices argument to widgets."""
        return _get_choices(cls)

    @classmethod
    def validator(cls, value):
        invalid = value < 0
        msg_text = _('{value} is not a valid {class_name}')
        if not invalid:
            try:
                cls(value)
            except ValueError:
                invalid = True
        if invalid:
            raise ValidationError(
                msg_text.format(value=value, class_name=cls.__name__)
            )

    @property
    def selected_list(self):
        """Return component flag values as list of strings."""
        selected = [
            str(f.value) for f in self.__class__ if self & f
        ]
        return selected

    def __contains__(self, flag: 'ModelFlag') -> bool:  # noqa: F821
        """Indicate whether this ModelFlag is a (possibly equal) superset of
        its argument.

        This implementation differs from Flag.__contains__() by allowing
        ModelFlag(0) to be contained in any valid ModelFlag - including itself.
        """
        return bool(self & flag) and self & flag == flag
