from ..rules.external import ExternallyExecutedRegexRule, ExternallyExecutedWordlistRule


def test_ee_regex(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = ExternallyExecutedRegexRule(expression="test", endpoint=url, censor_token="<censored>")

    # Act
    result = list(rule.match("This is a test"))

    # Assert
    assert len(result) == 1
    assert result[0]['context'] == "This is a <censored>"


def test_ee_regex_confidentely_wrong(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 0, "confidence": 1.00})

    rule = ExternallyExecutedRegexRule(expression="test", endpoint=url, censor_token="<censored>")

    # Act
    result = list(rule.match("This is a test"))

    # Assert
    assert len(result) == 0


def test_ee_regex_insecure(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 0.15})

    rule = ExternallyExecutedRegexRule(expression="test", endpoint=url, censor_token="<censored>")

    # Act
    result = list(rule.match("This is a test"))

    # Assert
    assert len(result) == 0


def test_ee_regex_no_match(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = ExternallyExecutedRegexRule(expression="exam", endpoint=url, censor_token="<censored>")

    # Act
    result = list(rule.match("This is a test"))

    # Assert
    assert len(result) == 0


def test_ee_regex_censor_multiple(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = ExternallyExecutedRegexRule(expression="test", endpoint=url, censor_token="<censored>")

    # Act
    result = list(rule.match("testing, one two three, testing"))

    # Assert
    assert len(result) == 1
    assert result[0]['context'] == "<censored>ing, one two three, <censored>ing"


def test_ee_wordlist(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = ExternallyExecutedWordlistRule(
        "en_20211018_unit_test_words",
        endpoint=url,
        censor_token="<sundhedsterm>",
    )

    # Act
    result = list(rule.match("Kol er noget farligt noget"))

    # Assert
    assert len(result) == 1
    assert result[0]['context'] == "<sundhedsterm> er noget farligt noget"


def test_ee_wordlist_confidentely_incorrect(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 0, "confidence": 1.00})

    rule = ExternallyExecutedWordlistRule(
        "en_20211018_unit_test_words",
        endpoint=url,
        censor_token="<sundhedsterm>",
    )

    # Act
    result = list(rule.match("Kol er noget farligt noget"))

    # Assert
    assert len(result) == 0


def test_ee_wordlist_insecure(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 0.15})

    rule = ExternallyExecutedWordlistRule(
        "en_20211018_unit_test_words",
        endpoint=url,
        censor_token="<sundhedsterm>",
    )

    # Act
    result = list(rule.match("Kol er noget farligt noget"))

    # Assert
    assert len(result) == 0


def test_ee_wordlist_no_match(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = ExternallyExecutedWordlistRule(
        "en_20211018_unit_test_words",
        endpoint=url,
        censor_token="<sundhedsterm>",
    )

    # Act
    result = list(rule.match("Ko er noget farligt noget"))

    # Assert
    assert len(result) == 0


def test_ee_wordlist_censor_multiple(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = ExternallyExecutedWordlistRule(
        "en_20211018_unit_test_words",
        endpoint=url,
        censor_token="<sundhedsterm>",
    )

    # Act
    result = list(rule.match("Jeg har både kol og pest"))

    # Assert
    assert len(result) == 1
    assert result[0]['context'] == "Jeg har både <sundhedsterm> og <sundhedsterm>"
