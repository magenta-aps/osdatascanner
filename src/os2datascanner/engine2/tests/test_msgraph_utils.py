"""
Unit tests for utilities for use with MS Graph.
"""

import requests
import pytest

from os2datascanner.engine2.model.msgraph import utilities as msgu
from os2datascanner.engine2.model.msgraph.graphiti import (baseclasses,
                                                           exceptions,
                                                           query_parameters)
from os2datascanner.engine2.model.msgraph.graphiti.builder import MSGraphURLBuilder


class MockHandler:
    def __init__(self):
        self._token = 1

    def _token_creator(self):
        self._token += 1

    @msgu.raw_request_decorator
    def handle(self):
        response = requests.Response()
        match self._token:
            case 1:
                response.status_code = 401
            case _:
                response.status_code = 200
        return response


class TestGraphUtilities:
    def test_rrd(self):
        """The raw_request_decorator function implements retry logic
        correctly."""

        handler = MockHandler()
        assert handler.handle().status_code == 200


@pytest.fixture
def builder():
    return MSGraphURLBuilder()


@pytest.fixture
def uid():
    return 'olsenbanden@microsoft.com'


@pytest.fixture
def gid():
    return 'olsenbandensfanklub'


@pytest.fixture
def did():
    return 'planer'


@pytest.fixture
def eid():
    return 'det-store-kup-mod-bang-johansen'


@pytest.fixture
def mfid():
    return 'hemmelige-oplysninger'


@pytest.fixture
def nid():
    return 'koden-til-pengeskabet'


class TestMSGraphURLBuilder:
    """
    Unit tests for the MSGraphURLBuilder utility class.
    """

    def test_default_builder_returns_base_url(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL

        # Act
        actual = builder.build()

        # Assert
        assert expected == actual

    def test_v1_endpoint(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0'

        # Act
        actual = builder.v1().build()

        # Assert
        assert expected == actual

    def test_beta_endpoint(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/beta'

        # Act
        actual = builder.beta().build()

        # Assert
        assert expected == actual

    def test_v1_me(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0/me'

        # Act
        actual = builder.v1().me().build()

        # Assert
        assert expected == actual

    def test_v1_me_calendar(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0/me/calendar'

        # Act
        actual = builder.v1().me().calendar().build()

        # Assert
        assert expected == actual

    def test_v1_me_calendar_groups(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0/me/calendarGroups'

        # Act
        actual = builder.v1().me().calendar_groups().build()

        # Assert
        assert expected == actual

    def test_v1_me_calendar_view(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0/me/calendarView'

        # Act
        actual = builder.v1().me().calendar_view().build()

        # Assert
        assert expected == actual

    def test_v1_me_drive(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0/me/drive'

        # Act
        actual = builder.v1().me().drive().build()

        # Assert
        assert expected == actual

    def test_v1_users_with_id(self, builder, uid):
        # Arrange
        expected = baseclasses.BASE_URL + f'/v1.0/users/{uid}'

        # Act
        actual = builder.v1().users(uid).build()

        # Assert
        assert expected == actual

    def test_v1_users_app_role_assignments(self, builder, uid):
        # Arrange
        expected = baseclasses.BASE_URL + f'/v1.0/users/{uid}/appRoleAssignments'

        # Act
        actual = builder.v1().users(uid).app_role_assignments().build()

        # Assert
        assert expected == actual

    def test_v1_users_calendars(self, builder, uid):
        # Arrange
        expected = baseclasses.BASE_URL + f'/v1.0/users/{uid}/calendars'

        # Act
        actual = builder.v1().users(uid).calendars().build()

        # Assert
        assert expected == actual

    def test_v1_users_drives(self, builder, uid, did):
        # Arrange
        expected = baseclasses.BASE_URL + f'/v1.0/users/{uid}/drives/{did}'

        # Act
        actual = builder.v1().users(uid).drives(did).build()

        # Assert
        assert expected == actual

    def test_v1_users_events(self, builder, uid, eid):
        # Arrange
        expected = baseclasses.BASE_URL + f'/v1.0/users/{uid}/events/{eid}'

        # Act
        actual = builder.v1().users(uid).events(eid).build()

        # Assert
        assert expected == actual

    def test_v1_users_mail_folders(self, builder, uid, mfid):
        # Arrange
        expected = baseclasses.BASE_URL + f'/v1.0/users/{uid}/mailFolders/{mfid}'

        # Act
        actual = builder.v1().users(uid).mail_folders(mfid).build()

        # Assert
        assert expected == actual

    def test_v1_users_onenote_notebook(self, builder, uid, nid):
        # Arrange
        expected = baseclasses.BASE_URL + f'/v1.0/users/{uid}/onenote/notebook/{nid}'

        # Act
        actual = builder.v1().users(uid).onenote().notebook(nid).build()

        # Assert
        assert expected == actual

    def test_v1_groups(self, builder, gid):
        # Arrange
        expected = baseclasses.BASE_URL + f'/v1.0/groups/{gid}'

        # Act
        actual = builder.v1().groups(gid).build()

        # Assert
        assert expected == actual

    def test_v1_groups_sites(self, builder, gid):
        # Arrange
        expected = baseclasses.BASE_URL + f'/v1.0/groups/{gid}/sites'

        # Act
        actual = builder.v1().groups(gid).sites().build()

        # Assert
        assert expected == actual

    def test_v1_sites_root(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0/sites/root'

        # Act
        actual = builder.v1().sites().root().build()

        # Assert
        assert expected == actual

    def test_v1_directory(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0/directory'

        # Act
        actual = builder.v1().directory().build()

        # Assert
        assert expected == actual

    def test_v1_directory_objects(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0/directoryObjects'

        # Act
        actual = builder.v1().directory_objects().build()

        # Assert
        assert expected == actual

    def test_v1_drive(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0/drive'

        # Act
        actual = builder.v1().drive().build()

        # Assert
        assert expected == actual

    def test_odata_build_empty(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0'

        # Act
        odata = query_parameters.ODataQueryBuilder()
        node = builder.v1()
        actual = odata.build(node)

        # Assert
        assert expected == actual

    def test_odata_build_count(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0?$count=true'

        # Act
        odata = query_parameters.ODataQueryBuilder().count(True)
        node = builder.v1()
        actual = odata.build(node)

        # Assert
        assert expected == actual

    def test_odata_build_count_top(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0?$count=true&$top=1'

        # Act
        odata = query_parameters.ODataQueryBuilder().count(True).top(1)
        node = builder.v1()
        actual = odata.build(node)

        # Assert
        assert expected == actual

    def test_odata_twice_raises_error(self):
        # Act & Assert
        with pytest.raises(exceptions.DuplicateODataParameterError):
            query_parameters.ODataQueryBuilder().count().count()

    def test_odata_count_invalid_type_raises_error(self):
        # Act & Assert
        with pytest.raises(ValueError):
            query_parameters.ODataQueryBuilder().count('invalid argument')

    def test_odata_count_remove_count_is_ok(self, builder):
        # Arrange
        expected = baseclasses.BASE_URL + '/v1.0?$count=true'

        # Act
        odata = query_parameters.ODataQueryBuilder().count().remove('count').count()
        node = builder.v1()
        actual = odata.build(node)

        # Assert
        assert expected == actual

    def test_odata_remove_invalid_key_type_raises_error(self):
        # Act & Assert
        with pytest.raises(ValueError):
            query_parameters.ODataQueryBuilder().remove(42)

    def test_odata_to_url_empty(self):
        # Arrange
        expected = ''

        # Act
        actual = query_parameters.ODataQueryBuilder().to_url()

        # Assert
        assert expected == actual

    def test_odata_to_url_count(self):
        # Arrange
        expected = '?$count=true'

        # Act
        actual = query_parameters.ODataQueryBuilder().count().to_url()

        # Assert
        assert expected == actual

    def test_odata_to_url_count_top(self):
        # Arrange
        expected = '?$count=true&$top=1'

        # Act
        actual = query_parameters.ODataQueryBuilder().count().top(1).to_url()

        # Assert
        assert expected == actual
