import json

from django.utils import timezone

from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
from os2datascanner.projects.report.reportapp.utils import create_alias_and_match_relations

# This is a real raw_matches field from test data. This could probably be done
# in a better way.
raw_matches_json_matched = json.loads('''
{
  "handle": {
    "path": "Flere sider.html",
    "type": "lo-object",
    "source": {
      "type": "lo",
      "handle": {
        "path": "/Flere sider.docx",
        "type": "web",
        "source": {
          "url": "http://nginx",
          "type": "web",
          "exclude": [],
          "sitemap": null
        },
        "referrer": {
          "path": "/",
          "type": "web",
          "source": {
            "url": "http://nginx",
            "type": "web",
            "exclude": [],
            "sitemap": null
          },
          "last_modified": null
        },
        "last_modified": null
      }
    }
  },
  "origin": "os2ds_matches",
  "matched": true,
  "matches": [
    {
      "rule": {
        "name": "CPR regel",
        "type": "cpr",
        "blacklist": [
          "tullstatistik",
          "fakturanummer",
          "p-nummer",
          "p-nr",
          "fak-nr",
          "customer-no",
          "p.nr",
          "faknr",
          "customer no",
          "dhk:tx",
          "bilagsnummer",
          "test report no",
          "tullstatistisk",
          "ordrenummer",
          "pnr",
          "protocol no.",
          "order number"
        ],
        "whitelist": [
          "cpr"
        ],
        "modulus_11": true,
        "sensitivity": 1000,
        "ignore_irrelevant": true
      },
      "matches": [
        {
          "match": "1111XXXXXX",
          "offset": 1,
          "context": "XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX",
          "probability": 1.0,
          "sensitivity": 1000,
          "context_offset": 1
        },
        {
          "match": "1111XXXXXX",
          "offset": 22,
          "context": "XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX",
          "probability": 1.0,
          "sensitivity": 1000,
          "context_offset": 22
        },
        {
          "match": "1111XXXXXX",
          "offset": 33,
          "context": "XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX",
          "probability": 1.0,
          "sensitivity": 1000,
          "context_offset": 33
        },
        {
          "match": "1111XXXXXX",
          "offset": 48,
          "context": "XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX",
          "probability": 1.0,
          "sensitivity": 1000,
          "context_offset": 48
        },
        {
          "match": "1111XXXXXX",
          "offset": 63,
          "context": "XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX",
          "probability": 1.0,
          "sensitivity": 1000,
          "context_offset": 50
        }
      ]
    }
  ],
  "scan_spec": {
    "rule": {
      "name": "CPR regel",
      "type": "cpr",
      "blacklist": [
        "tullstatistik",
        "fakturanummer",
        "p-nummer",
        "p-nr",
        "fak-nr",
        "customer-no",
        "p.nr",
        "faknr",
        "customer no",
        "dhk:tx",
        "bilagsnummer",
        "test report no",
        "tullstatistisk",
        "ordrenummer",
        "pnr",
        "protocol no.",
        "order number"
      ],
      "whitelist": [
        "cpr"
      ],
      "modulus_11": true,
      "sensitivity": 1000,
      "ignore_irrelevant": true
    },
    "source": {
      "type": "lo",
      "handle": {
        "path": "/Flere sider.docx",
        "type": "web",
        "source": {
          "url": "http://nginx",
          "type": "web",
          "exclude": [],
          "sitemap": null
        },
        "referrer": {
          "path": "/",
          "type": "web",
          "source": {
            "url": "http://nginx",
            "type": "web",
            "exclude": [],
            "sitemap": null
          },
          "last_modified": null
        },
        "last_modified": null
      }
    },
    "progress": null,
    "scan_tag": {
      "time": "2023-01-05T11:32:26+01:00",
      "user": "dev",
      "scanner": {
        "pk": 2,
        "name": "Local nginx",
        "test": false
      },
      "destination": "pipeline_collector",
      "organisation": {
        "name": "OS2datascanner",
        "uuid": "0e18b3f2-89b6-4200-96cd-38021bbfa00f"
      }
    },
    "filter_rule": null,
    "configuration": {
      "skip_mime_types": [
        "image/*"
      ]
    }
  }
}
''')

raw_problem_json = json.loads('''
{
   "handle":{
      "path":"Sammenl%E6gningsudvalget",
      "type":"smbc",
      "hints":null,
      "source":{
         "unc":"//samba/e2test",
         "type":"smbc",
         "user":null,
         "domain":null,
         "password":null,
         "driveletter":null,
         "unc_is_home_root":false,
         "skip_super_hidden":false
      }
   },
   "origin":"os2ds_problems",
   "source":{
      "unc":"//samba/e2test",
      "type":"smbc",
      "user":null,
      "domain":null,
      "password":null,
      "driveletter":null,
      "unc_is_home_root":false,
      "skip_super_hidden":false
   },
   "message":"Exploration error. MemoryError: 12, Cannot allocate memory",
   "missing":false,
   "scan_tag":{
      "time":"2024-08-15T08:27:20+02:00",
      "user":"dev",
      "scanner":{
         "pk":1,
         "name":"Lille Samba",
         "test":false,
         "keep_fp":true
      },
      "destination":"pipeline_collector",
      "organisation":{
         "name":"OSdatascanner",
         "uuid":"365ddcab-c998-466e-b3fa-d8ed124a349d"
      }
   }
}
''')

raw_problem2_json = json.loads('''
{
   "handle":{
      "path":"Sammenl%E6gningsudvalget",
      "type":"smbc",
      "hints":null,
      "source":{
         "unc":"//samba/e2test",
         "type":"smbc",
         "user":null,
         "domain":null,
         "password":null,
         "driveletter":null,
         "unc_is_home_root":false,
         "skip_super_hidden":false
      }
   },
   "origin":"os2ds_problems",
   "source":{
      "unc":"//samba/e2test",
      "type":"smbc",
      "user":null,
      "domain":null,
      "password":null,
      "driveletter":null,
      "unc_is_home_root":false,
      "skip_super_hidden":false
   },
   "message":"Unknown Error: This is definitely an error",
   "missing":false,
   "scan_tag":{
      "time":"2024-08-15T08:27:20+02:00",
      "user":"dev",
      "scanner":{
         "pk":1,
         "name":"Lille Samba",
         "test":false,
         "keep_fp":true
      },
      "destination":"pipeline_collector",
      "organisation":{
         "name":"OSdatascanner",
         "uuid":"365ddcab-c998-466e-b3fa-d8ed124a349d"
      }
   }
}
''')


def create_reports_for(alias,  # noqa: CCR001 Cognitive complexity
                       num=10,
                       scanner_job_pk=1,
                       scanner_job_name="Local nginx",
                       sensitivity=1000,
                       datasource_last_modified=timezone.now(),
                       resolution_status=None,
                       only_notify_superadmin=False,
                       created_at=None,
                       matched=True,
                       problem=False):
    pks = []
    for i in range(num):
        if problem == 1:
            problem_message = raw_problem_json
        elif problem == 2:
            problem_message = raw_problem2_json
        else:
            problem_message = None

        dr = DocumentReport.objects.create(
            name=f"Report-{i}{'-matched' if matched else ''}",
            owner=alias._value,
            scanner_job_pk=scanner_job_pk,
            scanner_job_name=scanner_job_name,
            sensitivity=sensitivity,
            datasource_last_modified=datasource_last_modified,
            path=(f"report-{i}-{scanner_job_pk}-{alias.account.username}"
                  f"-{'matched' if matched else 'unmatched'}-{alias._alias_type}"
                  f":{alias._value}-s{sensitivity}-dlm{datasource_last_modified}"
                  f"-ca{created_at if created_at else 'None'}"
                  f"-prob{problem if problem else 'None'}"
                  f"-rs{resolution_status if resolution_status is not None else 'None'}"),
            raw_matches=raw_matches_json_matched if matched else None,
            organization=alias.account.organization,
            resolution_status=resolution_status,
            only_notify_superadmin=only_notify_superadmin,
            raw_problem=problem_message)
        pks.append(dr.pk)
    if created_at:
        DocumentReport.objects.filter(pk__in=pks).update(created_timestamp=created_at)

    create_alias_and_match_relations(alias)
