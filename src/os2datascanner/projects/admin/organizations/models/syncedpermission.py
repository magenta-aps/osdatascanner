# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from os2datascanner.core_organizational_structure.models import \
    SyncedPermission as CoreSyncedPermission


class SyncedPermission(CoreSyncedPermission):
    """Implemented here so the model exists in the admin module."""
