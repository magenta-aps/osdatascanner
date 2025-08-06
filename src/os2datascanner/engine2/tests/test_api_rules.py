from os2datascanner.engine2.rules.api import APIRegexRule, APIWordlistRule


def test_api_regex(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = APIRegexRule(expression="test", endpoint=url, censor_token="<censored>")

    # Act
    result = list(rule.match("This is a test"))

    # Assert
    assert len(result) == 1
    assert result[0]['context'] == "This is a <censored>"


def test_api_regex_confidentely_wrong(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 0, "confidence": 1.00})

    rule = APIRegexRule(expression="test", endpoint=url, censor_token="<censored>")

    # Act
    result = list(rule.match("This is a test"))

    # Assert
    assert len(result) == 0


def test_api_regex_insecure(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 0.15})

    rule = APIRegexRule(expression="test", endpoint=url, censor_token="<censored>")

    # Act
    result = list(rule.match("This is a test"))

    # Assert
    assert len(result) == 0


def test_api_regex_no_match(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = APIRegexRule(expression="exam", endpoint=url, censor_token="<censored>")

    # Act
    result = list(rule.match("This is a test"))

    # Assert
    assert len(result) == 0


def test_api_regex_censor_multiple(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = APIRegexRule(expression="test", endpoint=url, censor_token="<censored>")

    # Act
    result = list(rule.match("testing, one two three, testing"))

    # Assert
    assert len(result) == 1
    assert result[0]['context'] == "<censored>ing, one two three, <censored>ing"


def test_api_wordlist(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = APIWordlistRule(
        "en_20211018_unit_test_words",
        endpoint=url,
        censor_token="<sundhedsterm>",
    )

    # Act
    result = list(rule.match("Kol er noget farligt noget"))

    # Assert
    assert len(result) == 1
    assert result[0]['context'] == "<sundhedsterm> er noget farligt noget"


def test_api_wordlist_confidentely_incorrect(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 0, "confidence": 1.00})

    rule = APIWordlistRule(
        "en_20211018_unit_test_words",
        endpoint=url,
        censor_token="<sundhedsterm>",
    )

    # Act
    result = list(rule.match("Kol er noget farligt noget"))

    # Assert
    assert len(result) == 0


def test_api_wordlist_insecure(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 0.15})

    rule = APIWordlistRule(
        "en_20211018_unit_test_words",
        endpoint=url,
        censor_token="<sundhedsterm>",
    )

    # Act
    result = list(rule.match("Kol er noget farligt noget"))

    # Assert
    assert len(result) == 0


def test_api_wordlist_no_match(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = APIWordlistRule(
        "en_20211018_unit_test_words",
        endpoint=url,
        censor_token="<sundhedsterm>",
    )

    # Act
    result = list(rule.match("Ko er noget farligt noget"))

    # Assert
    assert len(result) == 0


def test_api_wordlist_censor_multiple(requests_mock):
    # Arrange
    url = 'http://fake-endpoint.test/predict'
    requests_mock.get(url, json={"prediction": 1, "confidence": 1.00})

    rule = APIWordlistRule(
        "en_20211018_unit_test_words",
        endpoint=url,
        censor_token="<sundhedsterm>",
    )

    # Act
    result = list(rule.match("Jeg har både kol og pest"))

    # Assert
    assert len(result) == 1
    assert result[0]['context'] == "Jeg har både <sundhedsterm> og <sundhedsterm>"
