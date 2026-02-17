# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from django.contrib.auth.models import AnonymousUser

from ..reportapp.views.report_views import UserReportView


@pytest.mark.django_db
class TestLoginRequired:

    def test_index_anonymous_user(self, rf):
        # Tries to hit path "/" with no login
        request = rf.get('/')
        request.user = AnonymousUser()
        response = UserReportView.as_view()(request)
        assert response.status_code == 302

    def test_index_as_user(self, rf, egon_account):
        # Tries to hit path "/" as user
        request = rf.get('/')
        user = egon_account.user
        request.user = user
        response = UserReportView.as_view()(request)

        # Should get status code 200 OK and report_content--personal.html template
        assert response.status_code == 200
        assert "report_content--personal.html" in response.template_name
