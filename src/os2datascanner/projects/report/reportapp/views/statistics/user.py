#!/usr/bin/env python
# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, render

from ....organizations.models.account import Account


class UserStatisticsPageView(LoginRequiredMixin, DetailView):
    template_name = "user_statistics_template.html"
    model = Account
    context_object_name = "account"

    def get_object(self, queryset=None):
        if self.kwargs.get(self.pk_url_kwarg) is None:
            try:
                self.kwargs[self.pk_url_kwarg] = self.request.user.account.uuid
            except Account.DoesNotExist:
                raise Http404()
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        account = context["account"]
        matches_by_week = account.count_matches_by_week()
        context["matches_by_week"] = matches_by_week

        scannerjobs = account.get_scannerjobs_list()
        context["scannerjobs"] = scannerjobs
        return context

    def post(self, request, *args, **kwargs):

        pk = kwargs.get("pk")
        self.verify_access(request.user, pk)

        # Check user permission
        if not request.user.has_perm("os2datascanner_report.delete_documentreport"):
            raise PermissionDenied

        scannerjob_pk = request.POST.get("pk")
        scannerjob_name = request.POST.get("name")
        account = Account.objects.get(pk=pk)

        reports = account.get_report(Account.ReportType.PERSONAL).filter(
                scanner_job__scanner_pk=scannerjob_pk)

        response_string = _(
            'You have deleted all results from %(scannerjob)s associated with '
            '%(account)s.'
        ) % {
            'scannerjob': scannerjob_name,
            'account': account.get_full_name(),
        }

        reports.delete()

        return render(
            request,
            "components/statistics/results_deleted.html", {
                "message": response_string
                })

    def get(self, request, *args, **kwargs):
        try:
            # If the URL has specified a primary key for the Account whose
            # statistics we want to see, then use that
            pk = kwargs.get("pk") or request.user.account.pk
        except Account.DoesNotExist:
            raise Http404()

        self.verify_access(request.user, pk)

        return super().get(request, *args, **kwargs)

    def verify_access(self, user, pk):
        target_account = get_object_or_404(Account, pk=pk)
        try:
            user_account = user.account
        except Account.DoesNotExist:
            user_account = None

        # (Note that accessing Account.user can't raise a DoesNotExist in the
        # way that User.account can, so we don't need to wrap this line)
        owned = target_account.user == user
        managed = user_account and target_account.managed_by(user_account)

        if user.is_superuser or owned or managed:
            return
        else:
            raise PermissionDenied
