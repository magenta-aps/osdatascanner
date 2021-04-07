from parameterized import parameterized
from django.test import TestCase

from ..models.position import Role


class RoleTest(TestCase):

    # TODO: this test should be generalized if the behaviour is moved out (see tests for ModelFlag)
    def test_choices(self):
        """The choices method returns the expected format."""
        expected = [
            ('employee', 'Employee'),
            ('manager', 'Manager'),
            ('dpo', 'Data protection officer')
        ]
        self.assertEqual(expected, Role.choices())
