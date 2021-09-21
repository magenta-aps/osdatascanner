#!/usr/bin/env python3
#
from django.utils.text import slugify
from os2datascanner.projects.admin.adminapp.models.authentication_model import (
    Authentication,
)
from os2datascanner.projects.admin.adminapp.models.scannerjobs.exchangescanner_model import (
    ExchangeScanner,
)
from os2datascanner.projects.admin.core.models.client import Client
from os2datascanner.projects.admin.organizations.models import (
    OrganizationalUnit,
    Account,
    Alias,
)
from os2datascanner.projects.admin.organizations.models.aliases import AliasType
from os2datascanner.projects.admin.organizations.models.organization import (
    Organization,
)

import uuid
import random

# Lets get some reproducibility
rd = random.Random()
rd.seed(0)


"""create OUs, Accounts, Aliases

Run
===
dsa='OS2DS_ADMIN_USER_CONFIG_PATH=$HOME/git/os2datascanner/dev-environment/admin/dev-settings.toml'
cd src/os2datascanner/projects/admin
dsa python ./manage.py runscript organizational_units [--script-args delete]


naming of OUs
=============
ou010: child of ou01. ou01 is child of ou0 and sister of ou00


Accounts (da: konti)
====================
These are the actual users that get scanned if they have a associated email Alias.
They are connected to OUs through a model.Position, which is implicit created when we
do account.units.add(OU)


List OUs using API and the UUID of the Organization
===================================================
Query admin/org-units-listing/?organization_id=UUID
example
-------
after running this script, do
http://localhost:8020/org-units-listing/?organization_id=5d02dfd3-b31c-4076-b2d5-4e41d3442952


Notes
=====
In case you want to see how this looks using the admin interface
- Remember to set your User as Administrator for client1
- Remember to activate Features and Allowed scantypes for client1


You might break your DB... YOLO! :)

runscript is from django-extension
https://django-extensions.readthedocs.io/en/latest/runscript.html
"""

client1, created = Client.objects.get_or_create(
    name="client1",
)
magenta_org, created = Organization.objects.get_or_create(
    name="Magenta ApS",
    uuid="5d02dfd3-b31c-4076-b2d5-4e41d3442952",
    slug=slugify("Magenta ApS"),
    client=client1,
)

hierarchies= [
    { # base OU, with Account
        "ou": "ou0",
        "ouid": uuid.UUID(int=rd.getrandbits(128)),
        "ou_parent": None,
        "aou": "a0ou0",
        "aid": uuid.UUID(int=rd.getrandbits(128)),
        "org": magenta_org,
        "email": True,
        "alias_id": uuid.UUID(int=rd.getrandbits(128)),
    },
    { # OU00, without Account
        "ou": "ou00",
        "ouid": uuid.UUID(int=rd.getrandbits(128)),
        "ou_parent": "ou0",
        "org": magenta_org,
    },
    { # OU000, with Account
        "ou": "ou000",
        "ouid": uuid.UUID(int=rd.getrandbits(128)),
        "ou_parent": "ou00",
        "aou": "a0ou000",
        "aid": uuid.UUID(int=rd.getrandbits(128)),
        "org": magenta_org,
        "email": True,
        "alias_id": uuid.UUID(int=rd.getrandbits(128)),
    },
    { # OU0001, with Account
        "ou": "ou001",
        "ouid": uuid.UUID(int=rd.getrandbits(128)),
        "ou_parent": "ou00",
        "aou": "a0ou001",
        "aid": uuid.UUID(int=rd.getrandbits(128)),
        "org": magenta_org,
        "email": True,
        "alias_id": uuid.UUID(int=rd.getrandbits(128)),
    },
    { # OU01. with Account
        "ou": "ou01",
        "ouid": uuid.UUID(int=rd.getrandbits(128)),
        "ou_parent": "ou0",
        "aou": "a0ou01",
        "aid": uuid.UUID(int=rd.getrandbits(128)),
        "org": magenta_org,
        "email": True,
        "alias_id": uuid.UUID(int=rd.getrandbits(128)),
    },
]

# store created objects
ous = {}
accounts = {}
aliases = {}


def run(*args):

    for h in hierarchies:
        # create OUs
        ou, created = OrganizationalUnit.objects.get_or_create(
            name=f"Test {h['ou']}",
            uuid=h["ouid"],
            parent=ous.get(h["ou_parent"]),
            organization=h["org"],
        )
        ous[h["ou"]] = ou

        if h.get("aou", False):
            # create accounts/konti
            account, created = Account.objects.get_or_create(
                uuid=h["aid"],
                username=h["aou"],
                first_name=f"first {h['aou']}",
                last_name=f"last {h['aou']}",
                organization=magenta_org,
            )
            accounts[h["aou"]] = account

        # create email-alias for account
        if h.get("email", False):
            alias, created = Alias.objects.get_or_create(
                uuid=h["alias_id"],
                account=account,
                value=f"{h['aou']}@{slugify(h['org'])}.dk",
            )
            alias.alias_type=AliasType.EMAIL
            alias.save()
            aliases[h["aou"]] = alias

        # connect Account to OU, through implicit model.Position which is created
        # when we do account.units.add(OU)
        account.units.add(ou)


    scanner_auth_obj, created = Authentication.objects.get_or_create(
        username="ImExchangeAdmin",
        domain="ThisIsMyExchangeDomain",
    )

    exchange_scan, created = ExchangeScanner.objects.get_or_create(
        # pk=3,
        name="This is an Exchange Scanner",
        organization=magenta_org,
        validation_status=ExchangeScanner.VALID,
        userlist="path/to/nothing.csv",
        service_endpoint="exchangeendpoint",
        authentication=scanner_auth_obj,
    )
    exchange_scan.org_unit.set(list(ous.values()))
    # XXX: If we don't explicit set this to a non-Null value, the admin interface
    # breaks.
    # The model Scanner.schedule have Null=True, but this doesn't work with the
    # web-interface
    exchange_scan.schedule = ""
    # XXX: what is this/why?
    exchange_scan.authentication.set_password("password")
    exchange_scan.save()

    ex_source = exchange_scan.generate_sources()

    sources = list(ex_source)
    users = [source.user for source in sources]
    alias_user = list(aliases.keys())

    print(f"generated {len(sources)} exchangeSources")
    print(f"going to scan users {users}")
    print(f"have aliases for {alias_user}")
    assert check_equal(users, alias_user), "ohh no. You broke it"

    if "delete" in args:
        #TODO, as we have past 30 years long ago, we are expected to be tidy...
        for ou in ous.values():
            ou.delete()


def check_equal(L1, L2):
    return len(L1) == len(L2) and sorted(L1) == sorted(L2)
