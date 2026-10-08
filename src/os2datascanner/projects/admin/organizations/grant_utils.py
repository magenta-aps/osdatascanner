# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

# Kept free of imports, so the forms and template tags can use these without import cycles.


def grant_permission_map(field_name: str) -> str:
    grant_permission_name_map = {
        "GraphGrant": "graphgrant",
        "graph_grant": "graphgrant",
        "SMBGrant": "smbgrant",
        "smb_grant": "smbgrant",
        "EWSGrant": "ewsgrant",
        "ews_grant": "ewsgrant",
        "GoogleApiGrant": "googleapigrant",
        "google_api_grant": "googleapigrant"
    }
    return grant_permission_name_map[field_name]


def grant_create_url_map(field_name: str) -> str:
    grant_create_url_names = {
        "smb_grant": "smbgrant-create",
        "ews_grant": "ewsgrant-create",
        "graph_grant": "msgraphgrant-create",
        "google_api_grant": "googleapigrant-create",
    }
    return grant_create_url_names[field_name]
