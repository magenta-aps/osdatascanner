# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from django.contrib.auth.models import Permission
from django.shortcuts import reverse


@pytest.mark.django_db
class TestUserErrorLogPermissions:

    @pytest.mark.parametrize('has_perm', [True, False])
    def test_view_usererrorlog(
            self,
            client,
            user_admin,
            basic_usererrorlog,
            basic_usererrorlog2,
            has_perm):
        if has_perm:
            user_admin.user_permissions.add(Permission.objects.get(codename="view_usererrorlog"))

        client.force_login(user_admin)
        url = reverse("error-log")
        response = client.get(url)

        if has_perm:
            assert response.status_code == 200
        else:
            assert response.status_code == 403
