import pytest
from ..rules.external import (
    ExternallyExecutedRegexRule,
    ExternallyExecutedWordlistRule,
    split_sentences,
)


@pytest.fixture
def external_regex_rule():
    return ExternallyExecutedRegexRule(
        expression="test",
        endpoint='http://fake-endpoint.test/predict',
        censor_token="<censored>",
        confidence_cutoff=0.40,
    )


@pytest.fixture
def external_wordlist_rule():
    return ExternallyExecutedWordlistRule(
        "en_20211018_unit_test_words",
        endpoint='http://fake-endpoint.test/predict',
        censor_token="<sundhedsterm>",
        confidence_cutoff=0.40,
    )


def test_ee_regex(requests_mock, external_regex_rule):
    # Arrange
    url = external_regex_rule.endpoint
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    # Act
    result = list(external_regex_rule.match("This is a test"))

    # Assert
    assert len(result) == 1
    assert result[0]['context'] == "This is a <censored>"


def test_ee_regex_insecure(requests_mock, external_regex_rule):
    # Arrange
    url = external_regex_rule.endpoint
    requests_mock.get(url, json={"prediction": 1, "confidence": 0.15})

    # Act
    result = list(external_regex_rule.match("This is a test"))

    # Assert
    assert len(result) == 0


def test_ee_regex_no_match(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = ExternallyExecutedRegexRule(
        expression="exam",
        endpoint=url,
        censor_token="<censored>",
        confidence_cutoff=0.40
    )

    # Act
    result = list(rule.match("This is a test"))

    # Assert
    assert len(result) == 0


def test_ee_regex_censor_multiple(requests_mock, external_regex_rule):
    # Arrange
    url = external_regex_rule.endpoint
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    # Act
    result = list(external_regex_rule.match("testing, one two three, testing"))

    # Assert
    assert len(result) == 1
    assert result[0]['context'] == "<censored>ing, one two three, <censored>ing"


def test_ee_wordlist(requests_mock, external_wordlist_rule):
    # Arrange
    url = external_wordlist_rule.endpoint
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    # Act
    result = list(external_wordlist_rule.match("Kol er noget farligt noget"))

    # Assert
    assert len(result) == 1
    assert result[0]['context'] == "<sundhedsterm> er noget farligt noget"


def test_ee_wordlist_insecure(requests_mock, external_wordlist_rule):
    # Arrange
    url = external_wordlist_rule.endpoint
    requests_mock.get(url, json={"prediction": 1, "confidence": 0.15})

    # Act
    result = list(external_wordlist_rule.match("Kol er noget farligt noget"))

    # Assert
    assert len(result) == 0


def test_ee_wordlist_no_match(requests_mock, external_wordlist_rule):
    # Arrange
    url = external_wordlist_rule.endpoint
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    # Act
    result = list(external_wordlist_rule.match("Ko er noget farligt noget"))

    # Assert
    assert len(result) == 0


def test_ee_wordlist_censor_multiple(requests_mock, external_wordlist_rule):
    # Arrange
    url = external_wordlist_rule.endpoint
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    # Act
    result = list(external_wordlist_rule.match("Jeg har både kol og pest"))

    # Assert
    assert len(result) == 1
    assert result[0]['context'] == "Jeg har både <sundhedsterm> og <sundhedsterm>"


def test_ee_split_sentences():
    # Arrange
    sentences = [
        "Egon havde en plan kl. 14.30.",
        "Benny ventede ved Nørrebrogade nr. 112.",
        "Kjeld blev stoppet af politiet ifm. røveriet."
    ]

    paragraph = " ".join(sentences)

    # Act
    result = list(split_sentences(paragraph))

    # Assert
    assert len(result) == 3
    assert sentences == result
