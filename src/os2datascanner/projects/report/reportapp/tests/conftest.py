import pytest


@pytest.fixture(scope="module")
def create_message():
    return {
        'time': '2024-04-04T15:18:17+02:00',
        'type': 'bulk_event_create',
        'publisher': 'admin',
        'classes': {
            'Organization': [
                {
                    'pk': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'name': 'Vejstrand'
                }
            ],
            'OrganizationalUnit': [
                {
                    'pk': '7f433229-a194-4778-8c50-289cc4d32df2',
                    'name': 'addev',
                    'parent': None,
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 1,
                    'rght': 12,
                    'tree_id': 1,
                    'level': 0
                },
                {
                    'pk': 'f40cfa85-1c5d-472c-bca0-e874c939aae3',
                    'name': 'ad',
                    'parent': '7f433229-a194-4778-8c50-289cc4d32df2',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 2,
                    'rght': 11,
                    'tree_id': 1,
                    'level': 1
                },
                {
                    'pk': 'ca1d1555-1afe-478f-adba-65d4ce706453',
                    'name': 'OSdatascanner',
                    'parent': 'f40cfa85-1c5d-472c-bca0-e874c939aae3',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 3,
                    'rght': 10,
                    'tree_id': 1,
                    'level': 2
                },
                {
                    'pk': '1fa5e11e-7661-4c9e-88f7-0b24bdd5d5ab',
                    'name': 'Magenta',
                    'parent': 'ca1d1555-1afe-478f-adba-65d4ce706453',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 4,
                    'rght': 9,
                    'tree_id': 1,
                    'level': 3
                },
                {
                    'pk': '93f62bd8-c042-4652-b1eb-7cd9e79f5502',
                    'name': 'Vejstrand',
                    'parent': '1fa5e11e-7661-4c9e-88f7-0b24bdd5d5ab',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 5,
                    'rght': 6,
                    'tree_id': 1,
                    'level': 4
                },
                {
                    'pk': '8b030967-c1f6-4006-982e-ad61c365ca15',
                    'name': 'Users',
                    'parent': '1fa5e11e-7661-4c9e-88f7-0b24bdd5d5ab',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 7,
                    'rght': 8,
                    'tree_id': 1,
                    'level': 4
                }
            ],
            'Account': [
                {
                    'pk': '1d381585-b443-457f-8d7f-e57fb6873aee',
                    'username': 'hilarious_harry',
                    'first_name': 'Harry',
                    'last_name': 'Laughalot',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'harry@haha.com'
                },
                {
                    'pk': '9de50285-9b18-4339-81e9-9712f2828cb7',
                    'username': 'smilingsusan',
                    'first_name': 'Susan',
                    'last_name': 'Chuckleworth',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'susan.smiles@lol.com'
                },
                {
                    'pk': '0d40519c-f7dc-4d0e-9166-63563eab4e6c',
                    'username': 'jokesjohnny',
                    'first_name': 'Johnny',
                    'last_name': 'Jokesmith',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'johnny@jokes.com'
                },
                {
                    'pk': '53c60487-e57b-4542-bd0c-82024dd78fcb',
                    'username': 'giggle_greg',
                    'first_name': 'Greg',
                    'last_name': 'Giggly',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'gigglegreg@giggle.com'
                },
                {
                    'pk': '5b5b818e-e6a1-4c5b-a388-efafa1c435f9',
                    'username': 'chuckle_charlie',
                    'first_name': 'Charlie',
                    'last_name': 'Chuckleson',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'charlie.chuckles@fun.com'
                },
                {
                    'pk': '558f8498-b422-45ea-8c3a-bd9bdbd3f603',
                    'username': 'gleeful_gary',
                    'first_name': 'Gary',
                    'last_name': 'Grinsworth',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': ''
                }
            ],
            'Position': [
                {
                    'pk': 1,
                    'account': '1d381585-b443-457f-8d7f-e57fb6873aee',
                    'unit': '93f62bd8-c042-4652-b1eb-7cd9e79f5502',
                    'role': 'employee'
                },
                {
                    'pk': 2,
                    'account': '9de50285-9b18-4339-81e9-9712f2828cb7',
                    'unit': '8b030967-c1f6-4006-982e-ad61c365ca15',
                    'role': 'employee'
                },
                {
                    'pk': 3,
                    'account': '0d40519c-f7dc-4d0e-9166-63563eab4e6c',
                    'unit': '8b030967-c1f6-4006-982e-ad61c365ca15',
                    'role': 'employee'
                },
                {
                    'pk': 4,
                    'account': '53c60487-e57b-4542-bd0c-82024dd78fcb',
                    'unit': '8b030967-c1f6-4006-982e-ad61c365ca15',
                    'role': 'employee'
                },
                {
                    'pk': 5,
                    'account': '5b5b818e-e6a1-4c5b-a388-efafa1c435f9',
                    'unit': '93f62bd8-c042-4652-b1eb-7cd9e79f5502',
                    'role': 'employee'
                },
                {
                    'pk': 6,
                    'account': '558f8498-b422-45ea-8c3a-bd9bdbd3f603',
                    'unit': '93f62bd8-c042-4652-b1eb-7cd9e79f5502',
                    'role': 'employee'
                }
            ],
            'Alias': [
                {
                    'pk': '6fe5e90b-dce7-4a92-b6fe-277c94c6c2d2',
                    'account': '1d381585-b443-457f-8d7f-e57fb6873aee',
                    '_value': 'harry@haha.com',
                    '_alias_type': 'email'
                },
                {
                    'pk': '680d2259-f7f4-4044-9150-f77e599063d1',
                    'account': '1d381585-b443-457f-8d7f-e57fb6873aee',
                    '_value': 'S-1-5-21-3408043864-3648112243-1231008302-9080',
                    '_alias_type': 'SID'
                },
                {
                    'pk': '2e298e3e-2c1b-4399-848c-b546a4c6989e',
                    'account': '9de50285-9b18-4339-81e9-9712f2828cb7',
                    '_value': 'S-1-5-21-3408043864-3648112243-1231008302-10335',
                    '_alias_type': 'SID'
                },
                {
                    'pk': 'f5e53783-8e9a-4f3b-b06a-15a18ac1bce5',
                    'account': '0d40519c-f7dc-4d0e-9166-63563eab4e6c',
                    '_value': 'johnny@jokes.com',
                    '_alias_type': 'email'
                },
                {
                    'pk': '28078874-eca1-40d3-b07c-e7315b9f8eb4',
                    'account': '0d40519c-f7dc-4d0e-9166-63563eab4e6c',
                    '_value': 'S-1-5-21-3408043864-3648112243-1231008302-9078',
                    '_alias_type': 'SID'
                },
                {
                    'pk': 'c335fbfe-2367-4b2e-aed9-2f2f39806a47',
                    'account': '53c60487-e57b-4542-bd0c-82024dd78fcb',
                    '_value': 'gigglegreg@giggle.com',
                    '_alias_type': 'email'
                },
                {
                    'pk': 'b14f4c12-4dd6-4b80-ac30-b675f9f592db',
                    'account': '53c60487-e57b-4542-bd0c-82024dd78fcb',
                    '_value': 'S-1-5-21-3408043864-3648112243-1231008302-9079',
                    '_alias_type': 'SID'
                },
                {
                    'pk': 'a82b7f90-8f59-4b79-bb3a-87a95de0e093',
                    'account': '5b5b818e-e6a1-4c5b-a388-efafa1c435f9',
                    '_value': 'charlie.chuckles@fun.com',
                    '_alias_type': 'email'
                },
                {
                    'pk': '8120ef33-207e-4c99-9575-4e2a985a058a',
                    'account': '558f8498-b422-45ea-8c3a-bd9bdbd3f603',
                    '_value': 'garygrins@example.com',
                    '_alias_type': 'email'
                }
            ]
        }
    }


@pytest.fixture(scope="module")
def create_message_account_body(create_message):
    return create_message.get("classes").get("Account")


@pytest.fixture(scope="module")
def create_message_alias_body(create_message):
    return create_message.get("classes").get("Alias")


@pytest.fixture(scope="module")
def create_message_ou_body(create_message):
    return create_message.get("classes").get("OrganizationalUnit")


@pytest.fixture(scope="module")
def create_message_position_body(create_message):
    return create_message.get("classes").get("Position")


@pytest.fixture(scope="module")
def create_message_org_body(create_message):
    return create_message.get("classes").get("Organization")


@pytest.fixture(scope="module")
def update_message_in_order():
    return {
        'time': '2024-04-04T15:18:17+02:00',
        'type': 'bulk_event_update',
        'publisher': 'admin',
        'classes': {
            'Organization': [
                {
                    'pk': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'name': 'Strandvej'
                }
            ],
            'OrganizationalUnit': [
                {
                    'pk': '7f433229-a194-4778-8c50-289cc4d32df2',
                    'name': 'addev',
                    'parent': None,
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 1,
                    'rght': 12,
                    'tree_id': 1,
                    'level': 0
                },
                {
                    'pk': 'f40cfa85-1c5d-472c-bca0-e874c939aae3',
                    'name': 'ad',
                    'parent': '7f433229-a194-4778-8c50-289cc4d32df2',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 2,
                    'rght': 11,
                    'tree_id': 1,
                    'level': 1
                },
                {
                    'pk': 'ca1d1555-1afe-478f-adba-65d4ce706453',
                    'name': 'OSdatascanner',
                    'parent': '1fa5e11e-7661-4c9e-88f7-0b24bdd5d5ab',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 3,
                    'rght': 10,
                    'tree_id': 1,
                    'level': 2
                },
                {
                    'pk': '1fa5e11e-7661-4c9e-88f7-0b24bdd5d5ab',
                    'name': 'Magenta',
                    'parent': 'ca1d1555-1afe-478f-adba-65d4ce706453',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 4,
                    'rght': 9,
                    'tree_id': 1,
                    'level': 3
                },
                {
                    'pk': '93f62bd8-c042-4652-b1eb-7cd9e79f5502',
                    'name': 'Strand',
                    'parent': '1fa5e11e-7661-4c9e-88f7-0b24bdd5d5ab',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 5,
                    'rght': 6,
                    'tree_id': 1,
                    'level': 4
                },
                {
                    'pk': '8b030967-c1f6-4006-982e-ad61c365ca15',
                    'name': 'Brugere',
                    'parent': '1fa5e11e-7661-4c9e-88f7-0b24bdd5d5ab',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 7,
                    'rght': 8,
                    'tree_id': 1,
                    'level': 4
                }
            ],
            'Account': [
                {
                    'pk': '1d381585-b443-457f-8d7f-e57fb6873aee',
                    'username': 'not_so_hilarious_harry',
                    'first_name': 'Harriot',
                    'last_name': 'Laughalittle',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'harry@sad.com'
                },
                {
                    'pk': '9de50285-9b18-4339-81e9-9712f2828cb7',
                    'username': 'cyringsusan',
                    'first_name': 'Sadsan',
                    'last_name': 'NoChuckle',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'susan.smiles@lol.com'
                },
                {
                    'pk': '0d40519c-f7dc-4d0e-9166-63563eab4e6c',
                    'username': 'poem_johnny',
                    'first_name': 'Johnny',
                    'last_name': 'Poems',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'johnny@poems.com'
                },
                {
                    'pk': '53c60487-e57b-4542-bd0c-82024dd78fcb',
                    'username': 'giggle_greg',
                    'first_name': 'Greggory',
                    'last_name': 'Giggly',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'gigglegreg@giggle.com'
                },
                {
                    'pk': '5b5b818e-e6a1-4c5b-a388-efafa1c435f9',
                    'username': 'chuckle_charlie_3rd',
                    'first_name': 'Charlie',
                    'last_name': 'Chuckleson III',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'charlie.chuckles@fun.com'
                },
                {
                    'pk': '558f8498-b422-45ea-8c3a-bd9bdbd3f603',
                    'username': 'gleeful_gary',
                    'first_name': 'Gary Snail',
                    'last_name': 'Grinsworth',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'garygrins@example.com'
                }
            ],
            'Position': [
                {
                    'pk': 1,
                    'account': '1d381585-b443-457f-8d7f-e57fb6873aee',
                    'unit': '93f62bd8-c042-4652-b1eb-7cd9e79f5502',
                    'role': 'dpo'
                },
                {
                    'pk': 2,
                    'account': '9de50285-9b18-4339-81e9-9712f2828cb7',
                    'unit': '8b030967-c1f6-4006-982e-ad61c365ca15',
                    'role': 'manager'
                },
                {
                    'pk': 3,
                    'account': '0d40519c-f7dc-4d0e-9166-63563eab4e6c',
                    'unit': '8b030967-c1f6-4006-982e-ad61c365ca15',
                    'role': 'dpo'
                },
                {
                    'pk': 4,
                    'account': '53c60487-e57b-4542-bd0c-82024dd78fcb',
                    'unit': '8b030967-c1f6-4006-982e-ad61c365ca15',
                    'role': 'manager'
                },
                {
                    'pk': 5,
                    'account': '5b5b818e-e6a1-4c5b-a388-efafa1c435f9',
                    'unit': '93f62bd8-c042-4652-b1eb-7cd9e79f5502',
                    'role': 'dpo'
                },
                {
                    'pk': 6,
                    'account': '558f8498-b422-45ea-8c3a-bd9bdbd3f603',
                    'unit': '93f62bd8-c042-4652-b1eb-7cd9e79f5502',
                    'role': 'employee'
                }
            ],
            'Alias': [
                {
                    'pk': '6fe5e90b-dce7-4a92-b6fe-277c94c6c2d2',
                    'account': '1d381585-b443-457f-8d7f-e57fb6873aee',
                    '_value': 'harry@sad.com',
                    '_alias_type': 'email'
                },
                {
                    'pk': 'f5e53783-8e9a-4f3b-b06a-15a18ac1bce5',
                    'account': '0d40519c-f7dc-4d0e-9166-63563eab4e6c',
                    '_value': 'johnny@poems.com',
                    '_alias_type': 'email'
                },
            ]
        }
    }


@pytest.fixture(scope="module")
def update_message_account_body_in_order(update_message_in_order):
    return update_message_in_order.get("classes").get("Account")


@pytest.fixture(scope="module")
def update_message_alias_body_in_order(update_message_in_order):
    return update_message_in_order.get("classes").get("Alias")


@pytest.fixture(scope="module")
def update_message_ou_body_in_order(update_message_in_order):
    return update_message_in_order.get("classes").get("OrganizationalUnit")


@pytest.fixture(scope="module")
def update_message_position_body_in_order(update_message_in_order):
    return update_message_in_order.get("classes").get("Position")


@pytest.fixture(scope="module")
def update_message_org_body_in_order(update_message_in_order):
    return update_message_in_order.get("classes").get("Organization")


@pytest.fixture(scope="module")
def update_message_not_in_order():
    return {
        'time': '2024-04-04T15:18:17+02:00',
        'type': 'bulk_event_update',
        'publisher': 'admin',
        'classes': {
            'Organization': [
                {
                    'pk': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'name': 'Strandvej'
                }
            ],
            'OrganizationalUnit': [
                {
                    'pk': '7f433229-a194-4778-8c50-289cc4d32df2',
                    'name': 'addev',
                    'parent': None,
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 1,
                    'rght': 12,
                    'tree_id': 1,
                    'level': 0
                },
                {
                    'pk': '8b030967-c1f6-4006-982e-ad61c365ca15',
                    'name': 'Brugere',
                    'parent': '1fa5e11e-7661-4c9e-88f7-0b24bdd5d5ab',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 7,
                    'rght': 8,
                    'tree_id': 1,
                    'level': 4
                },
                {
                    'pk': '1fa5e11e-7661-4c9e-88f7-0b24bdd5d5ab',
                    'name': 'Magenta',
                    'parent': 'ca1d1555-1afe-478f-adba-65d4ce706453',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 4,
                    'rght': 9,
                    'tree_id': 1,
                    'level': 3
                },
                {
                    'pk': '93f62bd8-c042-4652-b1eb-7cd9e79f5502',
                    'name': 'Strand',
                    'parent': '1fa5e11e-7661-4c9e-88f7-0b24bdd5d5ab',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 5,
                    'rght': 6,
                    'tree_id': 1,
                    'level': 4
                },
                {
                    'pk': 'f40cfa85-1c5d-472c-bca0-e874c939aae3',
                    'name': 'ad',
                    'parent': '7f433229-a194-4778-8c50-289cc4d32df2',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 2,
                    'rght': 11,
                    'tree_id': 1,
                    'level': 1
                },
                {
                    'pk': 'ca1d1555-1afe-478f-adba-65d4ce706453',
                    'name': 'OSdatascanner',
                    'parent': '1fa5e11e-7661-4c9e-88f7-0b24bdd5d5ab',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'lft': 3,
                    'rght': 10,
                    'tree_id': 1,
                    'level': 2
                },

            ],
            'Account': [
                {
                    'pk': '558f8498-b422-45ea-8c3a-bd9bdbd3f603',
                    'username': 'gleeful_gary',
                    'first_name': 'Gary Snail',
                    'last_name': 'Grinsworth',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'garygrins@example.com'
                },
                {
                    'pk': '0d40519c-f7dc-4d0e-9166-63563eab4e6c',
                    'username': 'poem_johnny',
                    'first_name': 'Johnny',
                    'last_name': 'Poems',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'johnny@poems.com'
                },
                {
                    'pk': '53c60487-e57b-4542-bd0c-82024dd78fcb',
                    'username': 'giggle_greg',
                    'first_name': 'Greggory',
                    'last_name': 'Giggly',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'gigglegreg@giggle.com'
                },
                {
                    'pk': '1d381585-b443-457f-8d7f-e57fb6873aee',
                    'username': 'not_so_hilarious_harry',
                    'first_name': 'Harriot',
                    'last_name': 'Laughalittle',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'harry@sad.com'
                },
                {
                    'pk': '9de50285-9b18-4339-81e9-9712f2828cb7',
                    'username': 'cyringsusan',
                    'first_name': 'Sadsan',
                    'last_name': 'NoChuckle',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'susan.smiles@lol.com'
                },
                {
                    'pk': '5b5b818e-e6a1-4c5b-a388-efafa1c435f9',
                    'username': 'chuckle_charlie_3rd',
                    'first_name': 'Charlie',
                    'last_name': 'Chuckleson III',
                    'organization': '0c4bab1f-1c54-4533-93c7-33cc0a5d4af1',
                    'manager': None,
                    'is_superuser': False,
                    'email': 'charlie.chuckles@fun.com'
                },

            ],
            'Position': [
                {
                    'pk': 6,
                    'account': '558f8498-b422-45ea-8c3a-bd9bdbd3f603',
                    'unit': '93f62bd8-c042-4652-b1eb-7cd9e79f5502',
                    'role': 'employee'
                },
                {
                    'pk': 4,
                    'account': '53c60487-e57b-4542-bd0c-82024dd78fcb',
                    'unit': '8b030967-c1f6-4006-982e-ad61c365ca15',
                    'role': 'manager'
                },
                {
                    'pk': 5,
                    'account': '5b5b818e-e6a1-4c5b-a388-efafa1c435f9',
                    'unit': '93f62bd8-c042-4652-b1eb-7cd9e79f5502',
                    'role': 'dpo'
                },
                {
                    'pk': 1,
                    'account': '1d381585-b443-457f-8d7f-e57fb6873aee',
                    'unit': '93f62bd8-c042-4652-b1eb-7cd9e79f5502',
                    'role': 'dpo'
                },
                {
                    'pk': 2,
                    'account': '9de50285-9b18-4339-81e9-9712f2828cb7',
                    'unit': '8b030967-c1f6-4006-982e-ad61c365ca15',
                    'role': 'manager'
                },
                {
                    'pk': 3,
                    'account': '0d40519c-f7dc-4d0e-9166-63563eab4e6c',
                    'unit': '8b030967-c1f6-4006-982e-ad61c365ca15',
                    'role': 'dpo'
                },

            ],
            'Alias': [
                {
                    'pk': 'f5e53783-8e9a-4f3b-b06a-15a18ac1bce5',
                    'account': '0d40519c-f7dc-4d0e-9166-63563eab4e6c',
                    '_value': 'johnny@poems.com',
                    '_alias_type': 'email'
                },
                {
                    'pk': '6fe5e90b-dce7-4a92-b6fe-277c94c6c2d2',
                    'account': '1d381585-b443-457f-8d7f-e57fb6873aee',
                    '_value': 'harry@sad.com',
                    '_alias_type': 'email'
                },

            ]
        }
    }


@pytest.fixture(scope="module")
def update_message_account_body_not_in_order(update_message_not_in_order):
    return update_message_not_in_order.get("classes").get("Account")


@pytest.fixture(scope="module")
def update_message_alias_body_not_in_order(update_message_not_in_order):
    return update_message_not_in_order.get("classes").get("Alias")


@pytest.fixture(scope="module")
def update_message_ou_body_not_in_order(update_message_not_in_order):
    return update_message_not_in_order.get("classes").get("OrganizationalUnit")


@pytest.fixture(scope="module")
def update_message_position_body_not_in_order(update_message_not_in_order):
    return update_message_not_in_order.get("classes").get("Position")


@pytest.fixture(scope="module")
def update_message_org_body_not_in_order(update_message_not_in_order):
    return update_message_not_in_order.get("classes").get("Organization")
