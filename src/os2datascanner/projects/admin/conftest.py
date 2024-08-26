import pytest

from uuid import UUID

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from os2datascanner.projects.grants.models import GraphGrant
from os2datascanner.engine2.model.file import (
    FilesystemHandle, FilesystemSource)
from os2datascanner.engine2.model.http import (
    WebHandle, WebSource)
from os2datascanner.engine2.pipeline.messages import (
    StatusMessage, ScanTagFragment,
    MatchesMessage, MatchFragment, ScanSpecMessage,
    ProblemMessage)
from os2datascanner.engine2.rules.regex import RegexRule

from os2datascanner.projects.admin.adminapp.models.rules import CustomRule, Sensitivity
from os2datascanner.core_organizational_structure.models.position import Role
from os2datascanner.projects.admin.organizations.models import (
    Organization, OrganizationalUnit, Account, Position, Alias)
from os2datascanner.projects.admin.core.models import Administrator, Client
from os2datascanner.projects.admin.adminapp.models.authentication import Authentication
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import Scanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import ScanStatus
from os2datascanner.projects.admin.adminapp.models.usererrorlog import UserErrorLog
from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner import WebScanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.exchangescanner import (
    ExchangeScanner)
from os2datascanner.projects.admin.adminapp.models.scannerjobs.msgraph import (
    MSGraphMailScanner)
from os2datascanner.projects.admin.tests.test_utilities import dummy_rule_dict


# SETTINGS OVERRIDE
@pytest.fixture
def temp_settings():
    return settings


@pytest.fixture
def USERERRORLOG_True(temp_settings):
    temp_settings.USERERRORLOG = True


# Users
@pytest.fixture
def anonymous_user():
    return AnonymousUser()


@pytest.fixture
def user():
    return get_user_model().objects.create(username='mr_userman', password='hunter2')


@pytest.fixture
def superuser(user):
    return get_user_model().objects.create(
        username='mr_superuserman',
        password='hunter2',
        is_superuser=True)


# First test organization
@pytest.fixture
def test_client():
    return Client.objects.create(name='test_client',
                                 contact_email="test@magenta.dk",
                                 contact_phone="12345678")


@pytest.fixture
def test_org(test_client):
    return Organization.objects.create(
        name='test_org',
        client=test_client,
        uuid=UUID("3d6d288f-b75f-43e2-be33-a43803cd1243"))


@pytest.fixture
def user_admin(test_org):
    user = get_user_model().objects.create(
        username='mr_useradmin', password='hunter2'
    )
    Administrator.objects.create(user=user, client=test_org.client)
    return user


@pytest.fixture
def basic_rule(test_org):
    rule = CustomRule.objects.create(**dummy_rule_dict)
    rule.organizations.add(test_org)
    return rule


@pytest.fixture
def org_rule(test_org):
    return CustomRule.objects.create(
        name="org_rule",
        description="org_rule",
        organization=test_org,
        sensitivity=Sensitivity.CRITICAL,
        _rule=RegexRule(r"[A-Z]{10}").to_json_object(),
    )


@pytest.fixture
def basic_scanner(test_org, basic_rule):
    return Scanner.objects.create(
            name=f"SomeScanner-{test_org.name}",
            organization=test_org,
            rule=basic_rule
        )


@pytest.fixture
def web_scanner(test_org, basic_rule):
    return WebScanner.objects.create(
        name=f"SomeWebScanner-{test_org.name}",
        organization=test_org,
        url="http://www.example.com/",
        rule=basic_rule
    )


@pytest.fixture
def invalid_web_scanner(test_org, basic_rule):
    return WebScanner.objects.create(
        name=f"InvalidWebScanner-{test_org.name}",
        organization=test_org,
        url="http://www.example.com/",
        validation_status=Scanner.INVALID,
        rule=basic_rule
    )


@pytest.fixture
def exchange_auth():
    return Authentication.objects.create(
        username="keyChainGuy",
        domain="dummydumbdumb.dumb",
    )


@pytest.fixture
def dummy_userlist():
    return SimpleUploadedFile("dummy.txt", b"aleph\nalex\nfred")


@pytest.fixture
def exchange_scanner(test_org, exchange_auth, basic_rule):
    return ExchangeScanner.objects.create(
        name=f"SomeExchangeScanner-{test_org.name}",
        organization=test_org,
        validation_status=ExchangeScanner.VALID,
        service_endpoint="exchangeendpoint",
        authentication=exchange_auth,
        rule=basic_rule
    )


@pytest.fixture
def exchange_scanner_with_userlist(test_org, dummy_userlist, exchange_auth, basic_rule):
    return ExchangeScanner.objects.create(
        name=f"SomeExchangeScanner-{test_org.name}",
        organization=test_org,
        validation_status=ExchangeScanner.VALID,
        userlist=dummy_userlist,
        service_endpoint="exchangeendpoint",
        authentication=exchange_auth,
        rule=basic_rule
    )


@pytest.fixture
def msgraph_grant(test_org):
    return GraphGrant.objects.create(
        organization=test_org,
        app_id="12345678-1234-1234-1234-123456789012",
        tenant_id="12345678-1234-1234-1234-123456789012",
        _client_secret="A very secret secret",
    )


@pytest.fixture
def msgraph_mailscanner(test_org, msgraph_grant, basic_rule):
    return MSGraphMailScanner.objects.create(
        name=f"SomeMSGraphMailScanner-{test_org.name}",
        organization=test_org,
        validation_status=MSGraphMailScanner.VALID,
        grant=msgraph_grant,
        rule=basic_rule
    )


@pytest.fixture
def arbitrary_time_string():
    return "2020-10-28T13:51:49+01:00"


@pytest.fixture
def basic_scan_tag(basic_scanner):
    return basic_scanner._construct_scan_tag()


@pytest.fixture
def web_scan_tag():
    return ScanTagFragment.make_dummy()


@pytest.fixture
def basic_status_message(basic_scan_tag):
    return StatusMessage(
        scan_tag=basic_scan_tag,
        message="basic_status_message"
    )


@pytest.fixture
def status_message_10_objects(basic_scan_tag):
    return StatusMessage(
        scan_tag=basic_scan_tag,
        message="status_message_10_objects",
        total_objects=10,
        status_is_error=False
    )


@pytest.fixture
def status_message_with_error(basic_scan_tag):
    return StatusMessage(
        scan_tag=basic_scan_tag,
        message="status_message_with_error",
        total_objects=0,
        status_is_error=True
    )


@pytest.fixture
def status_message_with_object_size(basic_scan_tag):
    return StatusMessage(
        scan_tag=basic_scan_tag,
        message="status_message_with_object_size",
        status_is_error=False,
        object_type="some_type",
        object_size=100
    )


@pytest.fixture
def status_messages(
        status_message_10_objects,
        status_message_with_error,
        status_message_with_object_size):
    return {status_message_10_objects.message: status_message_10_objects,
            status_message_with_error.message: status_message_with_error,
            status_message_with_object_size.message: status_message_with_object_size}


@pytest.fixture
def file_source():
    return FilesystemSource(
        "/mnt/fs01.magenta.dk/brugere/af"
    )


@pytest.fixture
def web_source():
    return WebSource(
        "https://www.example.com",
        sitemap="https://www.example.com/sitemap.xml",
        sitemap_trusted=True
    )


@pytest.fixture
def file_handle(file_source):
    return FilesystemHandle(
        file_source,
        "OS2datascanner/Dokumenter/Verdensherredømme - plan.txt"
    )


@pytest.fixture
def web_handle(web_source):
    return WebHandle(
        web_source,
        "path/to/resources.html",
        hints={
            "fresh": True,
            "last_modified": "2016-01-09T15:10:09-05:00"
        }
    )


@pytest.fixture
def corrupt_file_handle(file_source):
    return FilesystemHandle(
        file_source,
        "/logo/Flag/Gr\udce6kenland.jpg"
    )


@pytest.fixture
def file_scan_spec(basic_scan_tag, file_handle, basic_rule):
    return ScanSpecMessage(
        scan_tag=basic_scan_tag,
        source=file_handle.source,
        rule=basic_rule.make_engine2_rule(),
        configuration={},
        filter_rule=None,
        progress=None
    )


@pytest.fixture
def web_scan_spec(web_scan_tag, web_handle, basic_rule):
    return ScanSpecMessage(
        scan_tag=web_scan_tag,
        source=web_handle.source,
        rule=basic_rule.make_engine2_rule(),
        configuration={},
        filter_rule=None,
        progress=None
    )


@pytest.fixture
def corrupt_scan_spec(basic_scan_tag, corrupt_file_handle, basic_rule):
    return ScanSpecMessage(
        scan_tag=basic_scan_tag,
        source=corrupt_file_handle.source,
        rule=basic_rule.make_engine2_rule(),
        configuration={},
        filter_rule=None,
        progress=None
    )


@pytest.fixture
def positive_web_match_message(web_scan_spec, web_handle, basic_rule):
    return MatchesMessage(
        scan_spec=web_scan_spec,
        handle=web_handle,
        matched=True,
        matches=[
            MatchFragment(
                rule=basic_rule.make_engine2_rule(),
                matches=[{"dummy": "match object"}]
            )
        ]
    )


@pytest.fixture
def positive_corrupt_match_message(corrupt_scan_spec, corrupt_file_handle, basic_rule):
    return MatchesMessage(
        scan_spec=corrupt_scan_spec,
        handle=corrupt_file_handle,
        matched=True,
        matches=[
            MatchFragment(
                rule=basic_rule.make_engine2_rule(),
                matches=[{"dummy": "match object"}]
            )
        ]
    )


@pytest.fixture
def basic_problem_message(basic_scan_tag, file_handle, basic_rule):
    return ProblemMessage(
        scan_tag=basic_scan_tag,
        handle=file_handle,
        source=file_handle.source,
        message="basic error message"
    )


@pytest.fixture
def basic_scanstatus(basic_scanner):
    return ScanStatus.objects.create(
        scanner=basic_scanner,
        scan_tag=basic_scanner._construct_scan_tag().to_json_object())


@pytest.fixture
def web_scanstatus(web_scanner):
    return ScanStatus.objects.create(
        scanner=web_scanner,
        scan_tag=web_scanner._construct_scan_tag().to_json_object())


@pytest.fixture
def basic_scanstatus_completed(basic_scanner):
    return ScanStatus.objects.create(
        scanner=basic_scanner,
        scan_tag=basic_scanner._construct_scan_tag().to_json_object(),
        total_sources=1,
        total_objects=1,
        explored_sources=1,
        scanned_objects=1)


@pytest.fixture
def basic_usererrorlog(basic_scanstatus, test_org):
    return UserErrorLog.objects.create(
        scan_status=basic_scanstatus,
        path="GiveMeTheMoney",
        error_message="Something went awry!",
        engine_error="TestError: Test was just a test!",
        organization=test_org,
        is_new=True
    )


@pytest.fixture
def a_lot_of_usererrorlogs(basic_scanstatus, test_org):

    import random

    def random_string():
        return ''.join([random.choice("qwertyuiopasdfghjklzxcvbnm") for _ in range(10)])

    return UserErrorLog.objects.bulk_create([
        UserErrorLog(
            scan_status=basic_scanstatus,
            path=random_string(),
            error_message=random_string(),
            engine_error=f"TestError: {random_string()}",
            organization=test_org,
            is_new=True
        ) for _ in range(20)
    ])


# Test accounts and organizational units for test organization
@pytest.fixture
def familien_sand(test_org):
    return OrganizationalUnit.objects.create(name="Familien Sand", organization=test_org)


@pytest.fixture
def nisserne(test_org):
    return OrganizationalUnit.objects.create(name="Nisserne", organization=test_org)


@pytest.fixture
def nisserne_accounts(nisserne):
    return nisserne.account_set.all()


@pytest.fixture
def oluf(test_org, familien_sand):
    oluf = Account.objects.create(
        username="kartoffeloluf",
        first_name="Oluf",
        last_name="Sand",
        organization=test_org)
    oluf.units.add(familien_sand)
    return oluf


@pytest.fixture
def gertrud(test_org, familien_sand):
    gertrud = Account.objects.create(
        username="gertrud",
        first_name="Gertrud",
        last_name="Sand",
        organization=test_org)
    gertrud.units.add(familien_sand)
    return gertrud


@pytest.fixture
def benny(test_org):
    return Account.objects.create(
        username="benny",
        first_name="Benny",
        last_name="Jensen",
        organization=test_org)


@pytest.fixture
def fritz(test_org, nisserne):
    fritz = Account.objects.create(
        username="fritz",
        first_name="Fritz",
        organization=test_org,
        email="fritz@nisserne.gl")
    fritz.units.add(nisserne)
    return fritz


@pytest.fixture
def fritz_email_alias(fritz):
    return Alias.objects.create(
        account=fritz,
        _alias_type="email",
        _value="fritz@nisserne.gl",
        imported=True)


@pytest.fixture
def fritz_shared_email_alias(fritz):
    return Alias.objects.create(account=fritz, _alias_type="email", _value="all@nisserne.gl")


@pytest.fixture
def fritz_generic_alias(fritz):
    return Alias.objects.create(account=fritz, _alias_type="generic", _value="fritz.website")


@pytest.fixture
def fritz_remediator_alias(fritz, basic_scanner):
    return Alias.objects.create(account=fritz, _alias_type="remediator", _value=basic_scanner.pk)


@pytest.fixture
def günther(test_org, nisserne):
    günther = Account.objects.create(
        username="günther",
        first_name="Günther",
        organization=test_org)
    günther.units.add(nisserne)
    return günther


@pytest.fixture
def günther_email_alias(günther):
    return Alias.objects.create(
        account=günther,
        _alias_type="email",
        _value="günther@nisserne.gl",
        imported=True)


@pytest.fixture
def hansi(test_org, nisserne):
    hansi = Account.objects.create(username="hansi", first_name="Hansi", organization=test_org)
    hansi.units.add(nisserne)
    return hansi


@pytest.fixture
def hansi_email_alias(hansi):
    return Alias.objects.create(
        account=hansi,
        _alias_type="email",
        _value="hansi@nisserne.gl",
        imported=True)


@pytest.fixture
def gammel_nok(test_org):
    return Account.objects.create(
        username="gammelnok",
        first_name="Gammel",
        last_name="Nok",
        organization=test_org)


@pytest.fixture
def fritz_boss(fritz, nisserne):
    Position.objects.get_or_create(account=fritz, unit=nisserne, role=Role.EMPLOYEE)
    Position.objects.get_or_create(account=fritz, unit=nisserne, role=Role.MANAGER)
    Position.objects.get_or_create(account=fritz, unit=nisserne, role=Role.DPO)
    return fritz


# Additional test organizational units
@pytest.fixture
def bingoklubben(test_org):
    return OrganizationalUnit.objects.create(name="Bingoklubben", organization=test_org)


@pytest.fixture
def nørre_snede_if(test_org):
    return OrganizationalUnit.objects.create(name="Nørre Snede IF", organization=test_org)


@pytest.fixture
def kok_sokker(test_org):
    return OrganizationalUnit.objects.create(name="Kok-Sokker", organization=test_org)


@pytest.fixture
def dansk_kartoffelavlerforening(test_org):
    return OrganizationalUnit.objects.create(
        name="Dansk Kartoffelavlerforening",
        organization=test_org)


# Second test organization
@pytest.fixture
def test_org2():
    client = Client.objects.create(name='test_client2')
    return Organization.objects.create(name='test_org2', client=client)


@pytest.fixture
def org2_rule(test_org2):
    return CustomRule.objects.create(
        name="org2_rule",
        description="org2_rule",
        organization=test_org2,
        _rule=RegexRule(r"[A-Z]{10}").to_json_object(),
    )


@pytest.fixture
def other_admin(test_org2):
    user = get_user_model().objects.create(
        username='mr_otheradmin', password='hunter2'
    )
    Administrator.objects.create(user=user, client=test_org2.client)
    return user


@pytest.fixture
def olsen_banden(test_org2):
    return OrganizationalUnit.objects.create(
        name="Olsen Banden",
        organization=test_org2,
    )


@pytest.fixture
def egon(test_org2):
    return Account.objects.create(
        username="manden_med_planen",
        first_name="Egon",
        last_name="Olsen",
        organization=test_org2)


# Other scanner and ScanStatus fixtures with basic rule
@pytest.fixture
def basic_scanner2(test_org2, basic_rule):
    return Scanner.objects.create(
            name=f"SomeScanner-{test_org2.name}",
            organization=test_org2,
            rule=basic_rule
        )


@pytest.fixture
def web_scanner2(test_org2, basic_rule):
    return WebScanner.objects.create(
        name=f"SomeWebScanner-{test_org2.name}",
        organization=test_org2,
        url="http://www.example.com/",
        rule=basic_rule
    )


@pytest.fixture
def basic_scanstatus2(basic_scanner2):
    return ScanStatus.objects.create(
        scanner=basic_scanner2,
        scan_tag=basic_scanner2._construct_scan_tag().to_json_object())


@pytest.fixture
def basic_usererrorlog2(basic_scanstatus2, test_org2):
    return UserErrorLog.objects.create(
        scan_status=basic_scanstatus2,
        path="Don'tQuoteMeOnThis",
        error_message="Something went awry again!",
        engine_error="TestError: Test was still just a test!",
        organization=test_org2,
        is_new=True
    )
