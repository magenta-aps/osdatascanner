import requests
import structlog
from typing import Iterator, Optional

from .rule import Rule, Sensitivity
from .regex import RegexRule
from .wordlists import OrderedWordlistRule

logger = structlog.get_logger("engine2")


def get_prediction(sentence, endpoint) -> [int, int]:
    try:
        params = {
            'sentence': sentence,
            'version': 1,
        }
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        return int(data['prediction']), float(data['confidence'])
    except requests.RequestException as e:
        logger.debug("request failed", error=e)
        return 0, 0
    except (ValueError, KeyError) as e:
        logger.debug("error parsing response", error=e)
        return 0, 0


def split_sentences(content):
    delimiters = {'.'}
    max_sentence_length = 100
    current_sentence = ""
    for char in content:
        current_sentence += char
        if char in delimiters or len(current_sentence) >= max_sentence_length:
            yield current_sentence
            current_sentence = ""
    if current_sentence:
        yield current_sentence


class APIRegexRule(RegexRule):
    type_label = "api-regex"
    confidence_cutoff = 60

    def __init__(self, expression: str, endpoint: str, censor_token: str, **super_kwargs):
        self.endpoint = endpoint
        self.censor_token = censor_token
        super().__init__(expression, **super_kwargs)

    @property
    def presentation_raw(self) -> str:
        return f'regex matching "{self._expression}" contacting endpoint {self.endpoint}'

    def match(self, content: str) -> Optional[Iterator[dict]]:
        if not content:
            return

        for sentence in split_sentences(content):
            matches = list(super().match(sentence))
            if not matches:
                continue

            censored_sentence = sentence
            for m in matches:
                censored_sentence = censored_sentence.replace(m['match'], self.censor_token, 1)

            answer, confidence = get_prediction(censored_sentence, self.endpoint)
            if answer and confidence >= self.confidence_cutoff:
                yield {
                    "match": self.censor_token,
                    "sensitivity": (
                        self.sensitivity.value
                        if self.sensitivity else None
                    ),
                    "context": censored_sentence,
                }
                return

    def to_json_object(self) -> dict:
        return dict(
            **super().to_json_object(),
            endpoint=self.endpoint,
            censor_token=self.censor_token,
        )

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj: dict):
        return APIRegexRule(
            expression=obj["expression"],
            endpoint=obj["endpoint"],
            censor_token=obj["censor_token"],
            sensitivity=Sensitivity.make_from_dict(obj),
            name=obj["name"] if "name" in obj else None,
        )


class APIWordlistRule(OrderedWordlistRule):
    type_label = "api-wordlist"
    confidence_cutoff = 60

    def __init__(self, dataset: str, endpoint: str, censor_token: str, **super_kwargs):
        self.endpoint = endpoint
        self.censor_token = censor_token
        super().__init__(dataset, **super_kwargs)

    @property
    def presentation_raw(self) -> str:
        return f'words from "{self._dataset}", contacting endpoint {self.endpoint}'

    def match(self, content: str) -> Optional[Iterator[dict]]:
        if not content:
            return

        for sentence in split_sentences(content):
            matched = False
            censored_sentence = sentence
            for m in self._compiled_expr.finditer(sentence):
                lowered = str(m.group()).lower()
                if lowered in self._wordlists:
                    matched = True
                    censored_sentence = censored_sentence.replace(m.group(), self.censor_token, 1)
            if not matched:
                continue

            answer, confidence = get_prediction(censored_sentence, self.endpoint)
            if answer and confidence >= self.confidence_cutoff:
                yield {
                    "match": self.censor_token,
                    "sensitivity": (
                        self.sensitivity.value
                        if self.sensitivity else None
                    ),
                    "context": censored_sentence,
                }
                return

    def to_json_object(self) -> dict:
        return dict(
            **super().to_json_object(),
            endpoint=self.endpoint,
            censor_token=self.censor_token,
        )

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj: dict):
        return APIWordlistRule(
            dataset=obj["dataset"],
            endpoint=obj["endpoint"],
            censor_token=obj["censor_token"],
            sensitivity=Sensitivity.make_from_dict(obj),
            name=obj["name"] if "name" in obj else None,
        )
