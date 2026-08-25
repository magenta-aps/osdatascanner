#!/usr/bin/env python
# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import structlog

from django.shortcuts import redirect
from django.urls import reverse_lazy

from .utils import ResultsStatisticsPageView, StatisticsCSVExportMixin
from ....organizations.models.organizational_unit import OrganizationalUnit


logger = structlog.get_logger("reportapp")


class DPOStatisticsPageView(ResultsStatisticsPageView):
    template_name = "dpo_statistics_template.html"

    # TODO: We need to figure out multi tenancy. I.e. only view stuff from your organization

    def _get_own_units(self):
        if self.request.user.account.is_universal_dpo:
            return OrganizationalUnit.objects.filter(
                organization=self.request.user.account.organization)
        return self.request.user.account.get_dpo_units()

    def _confirm_orgunit_access(self, orgunit_uuid):
        return (self.request.user.account.get_dpo_units().filter(uuid=orgunit_uuid).exists()
                or self.request.user.account.is_universal_dpo)

    def dispatch(self, request, *args, **kwargs):

        response = super().dispatch(request, *args, **kwargs)

        try:
            # Allow the user access, if they are a superuser or has a DPO relation
            # to at least one organizational unit.
            if request.user.is_superuser or request.user.account.is_dpo:
                return response
        except Exception as e:
            logger.warning("Exception raised while trying to dispatch to user "
                           f"{request.user}: {e}")
        return redirect(reverse_lazy('index'))

    def count_match_status_by_org_unit(self):

        stats = OrganizationalUnit.objects.with_match_counts().filter(
            organization=self.request.user.account.organization
        ).values(
            "name", "total_ou_matches", "handled_ou_matches"
        )

        def get_matches(match_type):
            match match_type:
                case "unhandled":
                    props = ("name", "handled_ou_matches", "total_ou_matches")
                case "handled":
                    props = ("name", "handled_ou_matches")
                case "total":
                    props = ("name", "total_ou_matches")

            return [[ou.get(prop) for prop in props] for ou in stats]

        def sort_OU(array, match_type: str):
            def _key(x):
                match match_type, x:
                    case "unhandled", [_, handled_matches, match_count] if (
                            handled_matches is not None and match_count is not None):
                        return match_count - handled_matches
                    case "handled", [_, handled_matches] if handled_matches is not None:
                        return handled_matches
                    case "total", [_, match_count] if match_count is not None:
                        return match_count
                    case _:
                        return 0
            return sorted(array, key=_key)

        return tuple(list(reversed(sort_OU(get_matches(mt), match_type=mt)[-10:]))
                     for mt in ("unhandled", "handled", "total"))


class DPOStatisticsCSVView(StatisticsCSVExportMixin, DPOStatisticsPageView):
    exported_filename = 'osdatascanner_dpo_statistics'
    feature_flag_setting = 'DPO_CSV_EXPORT'
