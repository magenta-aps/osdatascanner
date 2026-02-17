# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""
Custom validators for form fields.
"""
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from os2datascanner.engine2.rules.rule import Rule as E2Rule
from os2datascanner.projects.admin.adminapp.views.utils.invariants import (
    RuleInvariantChecker,
    RuleInvariantViolationError,
)

# This is not the cleanest way to do translations, but django cannot detect what
# to translate from variables defined outside the django app, so this is
# probably the best we can do for now.
error_table = {
    "precedence":
    _("Cannot build rule: %(r1)s may not precede %(r2)s. Please change the order."),
    "standalone":
    _("Cannot build rule: %(r1)s must be used in conjunction with another rule."),
    "components":
    _("Cannot build rule: %(r1)s must include at least 2 components.")
}


def customrule_validator(value):
    """
    Builts the rule from json representation and applies
    invariant checks on the built rule. If any of the invariants
    fail, then a ValidationError is thrown.
    """
    checker = RuleInvariantChecker()

    try:
        rule = E2Rule.from_json_object(value)
    except Exception as e:
        raise ValidationError(f"Error occured while trying to construct rule: '{e}'")

    try:
        checker.check_invariants(rule)
    except RuleInvariantViolationError as rive:
        raise ValidationError(
            error_table.get(rive.message) % {f"r{i+1}": str(r)
                                             for i, r in enumerate(rive.rules)})
