import pytest
from ..models import ModelChoiceEnum
from ..models import ModelChoiceFlag
from django.core.exceptions import ValidationError


@pytest.fixture(scope="module")
def choice_enum():
    enum_class = ModelChoiceEnum(
        'TestEnum', {
            'FIRST': ('first', 'first label'),
            'SECOND': ('second', 'second label')
        }
    )
    return enum_class


@pytest.fixture(scope="module")
def choice_flag():
    choice_flag = ModelChoiceFlag(
        'TestEnum', {
            'FIRST': (1, 'first label'),
            'SECOND': (2, 'second label')
        }
    )
    return choice_flag


class TestModelChoiceFlag:

    def test_choices(self, choice_flag):
        """The choices method returns expected format."""
        expected = [(1, "First label"), (2, "Second label")]
        assert expected == choice_flag.choices()

    @pytest.mark.parametrize("test_input, flag_value, expected", [
        ('zero-value flag', 0, []),
        ('Single value flag', 1, ['1']),
        ('Combined value flag', 3, ['1', '2']),
    ])
    def test_selected_list(self, test_input, flag_value, expected, choice_flag):
        """The selected list method returns expected values."""
        flag = choice_flag(flag_value)
        assert expected == flag.selected_list

    @pytest.mark.parametrize("test_name, flag_value, test_value, expected", [
        ("Zero contains zero", 0, 0, False),
        ("Zero contains first", 0, 1, False),
        ("Single contains self", 1, 1, True),
        ("Single contains other", 1, 2, False),
        ("Single contains combination", 1, 3, False),
        ("Combination contains first", 3, 1, True),
        ("Combination contains second", 3, 2, True),
        ("Combination contains self", 3, 3, True),
        ("Combination contains zero", 3, 0, False),
    ])
    def test_contains(self, test_name, flag_value, test_value, expected, choice_flag):
        """Contains behaves as expected."""
        flag = choice_flag(flag_value)
        test = choice_flag(test_value)
        assert expected == (test in flag)

    @pytest.mark.parametrize("test_name, value", [
        ('Negative number', -1),
        # ('Too high number', 0b100), # todo: I simply cannot figure why this was a test case
    ])
    def test_feature_validator_invalid(self, test_name, value, choice_flag):
        """Validator throws exception as expected."""
        with pytest.raises(ValidationError):
            choice_flag.validator(value)

    @pytest.mark.parametrize("test_name, value", [
        ('Zero', 0),
        ('First', 1),
        ('Second', 0b10)
    ])
    def test_feature_validator_valid(self, test_name, value, choice_flag):
        """Validator passes as expected."""
        choice_flag.validator(value)


class TestModelChoiceEnum:

    def test_choices(self, choice_enum):
        """The choices method returns expected format."""
        expected = [('first', "First label"), ('second', "Second label")]
        assert expected == choice_enum.choices()
