import pytest
from django.db import connection
from django.db.models import Model, BooleanField
from django.db.utils import DatabaseError

from ..models.broadcasted_mixin import Broadcasted


@Broadcasted.register
class DummyBroadcastedModel(Model):
    test_field = BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'dummy_table'


@pytest.fixture
def dummy_broadcast_table():
    # Create the unmanaged model table
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(DummyBroadcastedModel)

        table_name = DummyBroadcastedModel._meta.db_table
        if table_name not in connection.introspection.table_names():
            raise DatabaseError(f"Table '{table_name}' is missing in test database")


@pytest.mark.django_db
class TestBroadcasted:
    def test_broadcasting_create(self, dummy_broadcast_table):
        assert DummyBroadcastedModel.objects.count() == 0
        DummyBroadcastedModel.objects.create()
        assert DummyBroadcastedModel.objects.count() == 1
