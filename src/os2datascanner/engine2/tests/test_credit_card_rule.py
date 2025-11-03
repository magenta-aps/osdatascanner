import pytest
from os2datascanner.engine2.rules.credit_card import CreditCardRule
from os2datascanner.engine2.rules import credit_card


@pytest.fixture
def valid_card():
    return "4539 1488 0343 6467"


@pytest.fixture
def invalid_card_extra_digit_after(valid_card):
    return valid_card + "1"


@pytest.fixture
def invalid_card_extra_digit_before(valid_card):
    return "1" + valid_card


@pytest.fixture
def groups_of_four_numbers(valid_card):
    """The middle of the groups of numbers is a valid card number"""
    return "1234 4321 " + valid_card + "6789 9876"


@pytest.fixture
def invalid_card():
    return "4111 1111 1111 1112"


@pytest.fixture
def valid_card_with_dash():
    return "4539-1488-0343-6467"


@pytest.fixture
def invalid_card_with_dash():
    return "4111-1111-1111-1112"


@pytest.fixture
def credit_card_rule():
    return CreditCardRule()


@pytest.fixture
def four_matches():
    return """4242424242424242, Lorem ipsum dolor sit amet, 4012888888881881.
    consectetur adipiscing elit. Sed non risus. 4539 1488 0343 6467.
    Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, 5555555555554444 ultricies sed,
    dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue,
    euismod non, mi."""


@pytest.fixture
def no_matches():
    return """Proin porttitor 4242424242424243, orci nec nonummy molestie,
    enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper 4012888888881882.
    Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim.
    Pellentesque congue 4111111111111112. Ut in risus volutpat libero pharetra tempor.
    Cras vestibulum bibendum augue 4000056655665557. """


@pytest.fixture
def wrong_number_of_digits():
    return "4222 2222 2222 2, 3782 822463 10005, 3056 9309 0259 04"


@pytest.fixture
def lots_of_numbers(valid_card):
    """The middle of the numbers are a valid card number"""
    return "12344321" + valid_card.replace(" ", "") + "67899876"


def test_luhn_algorithm_valid_card(valid_card):
    """ Checks that a valid credit card number will pass the luhn check. """
    # Arrange

    # Act
    actual_outcome = credit_card.luhn_algorithm(valid_card)

    # Assert
    assert actual_outcome


def test_luhn_algorithm_invalid_card(invalid_card):
    """ Checks that an invalid credit card number fails the luhn check. """
    # Arrange

    # Act
    actual_outcome = credit_card.luhn_algorithm(invalid_card)

    # Assert
    assert actual_outcome is False


def test_luhn_algorithm_valid_card_with_dash(valid_card_with_dash):
    """ Checks that a valid credit card number with dashes will pass the luhn check. """

    # Arrange

    # Act
    actual_outcome = credit_card.luhn_algorithm(valid_card_with_dash)

    # Assert
    assert actual_outcome


def test_luhn_algorithm_invalid_card_with_dash(invalid_card_with_dash):
    """ Checks that an invalid credit card number with dashes fails the luhn check. """

    # Arrange

    # Act
    actual_outcome = credit_card.luhn_algorithm(invalid_card_with_dash)

    # Assert
    assert actual_outcome is False


def test_match_with_one_match(valid_card, credit_card_rule):
    """ Checks that the match function considers a valid credit card number as valid. """
    # Arrange

    # Act
    expected_outcome = valid_card[:4] + "X"*12
    match = credit_card_rule.match(valid_card)
    for actual_outcome in match:
        # Assert
        assert expected_outcome == actual_outcome["match"]


def test_match_with_multiple_matches(four_matches, credit_card_rule):
    """ Checks that the match function is able to find multiple valid card numbers
    within a string. """

    # Arrange

    # Act
    expected_outcome = [
        "4242XXXXXXXXXXXX",
        "4012XXXXXXXXXXXX",
        "4539XXXXXXXXXXXX",
        "5555XXXXXXXXXXXX"]
    matches = credit_card_rule.match(four_matches)
    actual_outcome = []

    for match in matches:
        actual_outcome.append(match["match"])
    # Assert
    assert expected_outcome == actual_outcome


def test_match_with_no_match(no_matches, credit_card_rule):
    """ Checks that the match function won't consider any invalid credit card numbers within a
    string as valid. """

    # Arrange

    # Act
    actual_outcome = {}
    matches = credit_card_rule.match(no_matches)
    for match in matches:
        actual_outcome["match"] = match["match"]

    # Assert
    assert len(actual_outcome) == 0


def test_match_with_wrong_number_of_digits(wrong_number_of_digits, credit_card_rule):
    """ The purpose of this test is to make sure that the regex expression is working properly.
    The numbers from the wrong_number_of_digits fixture will pass the luhn_algorithm function,
    but they should not be accepted by the regex in the match function since it only accepts
    16 digit credit card numbers."""
    # Arrange

    # Act
    actual_outcome = {}
    matches = credit_card_rule.match(wrong_number_of_digits)
    for match in matches:
        actual_outcome["match"] = match["match"]

    # Assert
    assert len(actual_outcome) == 0


def test_card_with_extra_digit_before(invalid_card_extra_digit_before, credit_card_rule):
    """A valid credit card number with an extra digit prepended should not produce a match."""

    matches = [match for match in credit_card_rule.match(invalid_card_extra_digit_before)]

    assert len(matches) == 0


def test_card_with_extra_digit_after(invalid_card_extra_digit_after, credit_card_rule):
    """A valid credit card number with an extra digit appended should not produce a match."""

    matches = [match for match in credit_card_rule.match(invalid_card_extra_digit_after)]

    assert len(matches) == 0


def test_groups_of_four_numbers(groups_of_four_numbers, credit_card_rule):
    """A random assortment of groups of four numbers should not produce a match, even if a part
    of the groups is a valid credit card number."""

    """A valid credit card number with an extra digit prepended should not produce a match."""

    matches = [match for match in credit_card_rule.match(groups_of_four_numbers)]

    assert len(matches) == 0


def test_lots_of_numbers(lots_of_numbers, credit_card_rule):
    """A string of a lot of numbers should not produce a match, even if it partly contains a valid
    credit card number."""

    matches = [match for match in credit_card_rule.match(lots_of_numbers)]

    assert len(matches) == 0
