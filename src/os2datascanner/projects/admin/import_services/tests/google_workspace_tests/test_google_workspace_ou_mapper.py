import pytest
import uuid
from unittest.mock import MagicMock

from ...models.google_workspace_import_job import GoogleWorkspaceImportJob


@pytest.mark.django_db
def test_map_creates_hierarchy_and_names(test_org):
    """
    Tests that map_ous_to_models creates correct parent-child hierarchy,
    assigns organization and default names if name field is empty.
    """

    # Arrange
    job = GoogleWorkspaceImportJob(
        organization=test_org,
        delegated_admin_email="admin@email.com",
        )
    root_id = str(uuid.uuid4())
    child_id = str(uuid.uuid4())

    raw_ous = [
        {
            "orgUnitId": root_id,
            "name": "Root",
            "orgUnitPath": "/root",
            "parentOrgUnitId": None,
        },
        {
            "orgUnitId": child_id,
            "name": "",
            "orgUnitPath": "/root/child",
            "parentOrgUnitId": root_id,
        },
    ]

    client = MagicMock()
    client.list_organizational_units.return_value = raw_ous

    # Act
    (to_add, to_update, ou_map, imported_ids, parent_map), returned_raw_ous = (
        job._fetch_and_map_ous(client))

    # Assert
    assert returned_raw_ous == raw_ous

    root_imported_id = f"google-ou:{root_id}"
    child_imported_id = f"google-ou:{child_id}"

    root = ou_map[root_imported_id]
    child = ou_map[child_imported_id]

    assert parent_map[child_imported_id] == root_imported_id
    assert parent_map[root_imported_id] is None
    assert child.name == "child"
    assert root.name == "Root"
    assert len(to_add) == 2
    assert len(to_update) == 0
    assert root.organization == test_org
    assert child.organization == test_org
    assert root_imported_id in imported_ids
    assert child_imported_id in imported_ids


@pytest.mark.django_db
def test_mapper_is_idempotent(test_org):
    """
    Tests that map_ous_to_models is idempotent — running it twice with
    the same data returns the same model instance.
    """

    # Arrange
    job = GoogleWorkspaceImportJob(
        organization=test_org,
        delegated_admin_email="admin@example.com",
    )
    ou_id = str(uuid.uuid4())
    imported_id = f"google-ou:{ou_id}"

    raw = [
        {
            "orgUnitId": ou_id,
            "name": "Dept X",
            "orgUnitPath": "/DeptX",
            "parentOrgUnitId": None,
        }
    ]

    client = MagicMock()
    client.list_organizational_units.return_value = raw

    # Act
    (to_add1, to_update1, ou_map1, ids1, parent_map1), _ = job._fetch_and_map_ous(client)

    for ou in to_add1:
        ou.save()

    (to_add2, to_update2, ou_map2, ids2, parent_map2), _ = job._fetch_and_map_ous(client)

    # Assert
    assert ids1 == ids2
    assert list(ou_map1.keys()) == list(ou_map2.keys())

    o1 = ou_map1[imported_id]
    o2 = ou_map2[imported_id]

    assert o1.name == o2.name
    assert o1.organization == o2.organization
    assert len(to_add1) == 1
    assert len(to_update1) == 0
    assert len(to_add2) == 0
    assert len(to_update2) == 0
