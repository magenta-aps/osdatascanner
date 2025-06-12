import uuid
import pytest

from os2datascanner.projects.report.reportapp.views.utilities.ews_utilities \
        import find_exchange_grant

from os2datascanner.projects.grants.models import EWSGrant, GraphGrant


@pytest.fixture
def ews_grant_without_password(*, olsenbanden_organization):
    grant = EWSGrant(
            organization=olsenbanden_organization,
            username="benny@olsenbanden.dk")
    grant.password = ""
    grant.save()
    return grant


@pytest.fixture
def ews_grant_with_password(*, olsenbanden_organization):
    grant = EWSGrant(
            organization=olsenbanden_organization,
            username="egon@olsenbanden.dk")
    grant.password = "lad_os_saa_komme_i_g4ng"
    grant.save()
    return grant


@pytest.fixture
def another_ews_grant_with_password(*, olsenbanden_organization):
    grant = EWSGrant(
            organization=olsenbanden_organization,
            username="kjeld@olsenbanden.dk")
    grant.password = "nu_er_det_vel_ikke_f4rligt"
    grant.save()
    return grant


@pytest.fixture
def graph_grant_without_secret(*, olsenbanden_organization):
    grant = GraphGrant(
            organization=olsenbanden_organization,
            tenant_id=uuid.uuid4(), app_id=uuid.uuid4())
    grant.client_secret = ""
    grant.save()
    return grant


@pytest.fixture
def graph_grant_with_secret(
        *, graph_grant_without_secret):
    grant = graph_grant_without_secret
    grant.pk = None
    grant.tenant_id = uuid.uuid4()
    grant.client_secret = (
            "FAEHOVEDERGROEDBOENDERHAENGEROEVEIGNORANTERJAMMERKOMMODER")
    grant.save()
    return grant


@pytest.fixture
def another_graph_grant_with_secret(
        *, graph_grant_with_secret):
    grant = graph_grant_with_secret
    grant.pk = None
    grant.tenant_id = uuid.uuid4()
    grant.client_secret = "61CU5_Y[]3Dk`tVsCLxITX7e"
    grant.save()
    return grant


@pytest.mark.django_db
class TestMatchDeletion:
    def test_ews_grant_selection0(
            self, *,
            # Fixtures
            olsenbanden_organization,
            ews_grant_with_password,
            ews_grant_without_password):
        """Given an EWSGrant without a password and one with one, we should
        pick the one with a password."""
        assert (find_exchange_grant(olsenbanden_organization) ==
                (True, ews_grant_with_password))

    def test_ews_grant_selection1(
            self, *,
            # Fixtures
            olsenbanden_organization,
            ews_grant_with_password,
            ews_grant_without_password,
            graph_grant_without_secret):
        """Given an EWSGrant without a password, one with one, and a GraphGrant
        with no client secret, we should pick the EWSGrant with a password."""
        assert (find_exchange_grant(olsenbanden_organization) ==
                (True, ews_grant_with_password))

    def test_ews_grant_selection2(
            self, *,
            # Fixtures
            olsenbanden_organization,
            ews_grant_without_password,
            graph_grant_without_secret):
        """Given an EWSGrant without a password and a GraphGrant with no client
        secret, we should give up in despair."""
        assert (find_exchange_grant(olsenbanden_organization) ==
                (False, "no credentials available"))

    def test_ews_grant_selection3(
            self, *,
            # Fixtures
            olsenbanden_organization,
            ews_grant_without_password,
            graph_grant_with_secret):
        """Given an EWSGrant without a password and a GraphGrant with a client
        secret, we should pick the GraphGrant."""
        assert (find_exchange_grant(olsenbanden_organization) ==
                (True, graph_grant_with_secret))

    def test_ews_grant_selection4(
            self, *,
            olsenbanden_organization,
            ews_grant_with_password,
            graph_grant_with_secret):
        """Given an EWSGrant with a password and a GraphGrant with a client
        secret, we should pick the EWSGrant."""
        assert (find_exchange_grant(olsenbanden_organization) ==
                (True, ews_grant_with_password))

    def test_ews_grant_selection5(
            self, *,
            olsenbanden_organization,
            graph_grant_with_secret,
            another_graph_grant_with_secret):
        """Given two GraphGrants with client secrets, we should give up in
        paralysed indecision."""
        assert (find_exchange_grant(olsenbanden_organization) ==
                (False, "too many credentials available"))

    def test_ews_grant_selection6(
            self, *,
            olsenbanden_organization,
            ews_grant_with_password,
            another_ews_grant_with_password):
        """Given two EWSGrants with passwords, we should give up in
        paralysed indecision."""
        assert (find_exchange_grant(olsenbanden_organization) ==
                (False, "too many credentials available"))

    def test_ews_grant_selection7(
            self, *,
            olsenbanden_organization,
            ews_grant_with_password,
            graph_grant_with_secret,
            another_graph_grant_with_secret):
        """Given two GraphGrants with client secrets and a EWSGrant with a
        password, we should pick the EWSGrant."""
        assert (find_exchange_grant(olsenbanden_organization) ==
                (True, ews_grant_with_password))
