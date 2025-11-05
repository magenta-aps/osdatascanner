import requests
import structlog
import pysbd
from typing import Iterator, Optional

from .rule import Rule
from .regex import RegexRule
from .wordlists import OrderedWordlistRule
from .utilities.properties import RulePrecedence, RuleProperties

logger = structlog.get_logger("engine2")


def get_prediction(sentence, endpoint) -> [int, float]:
    """This helper method takes a `sentence` as a string, and an endpoint that should point
    to an available api. It will then call the api with the given sentence, and return
    - an integer, either 0 or 1, indicating whether or not the sentence is a match
    - a float, between 0 and 1, indicating the confidence that it is a match."""
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
    seg = pysbd.Segmenter(language="da", clean=True)

    for sentence in seg.segment(content):
        yield sentence


@Rule.register_class
class ExternallyExecutedRegexRule(RegexRule):
    type_label = "external-regex"

    def __init__(self,
                 expression: str,
                 endpoint: str,
                 censor_token: str,
                 confidence_cutoff: float,
                 **super_kwargs):
        self.endpoint = endpoint
        self.censor_token = censor_token
        self.confidence_cutoff = confidence_cutoff
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
            if confidence >= self.confidence_cutoff:
                yield {
                    "match": self.censor_token,
                    "sensitivity": self.sensitivity.value if self.sensitivity else None,
                    "context": censored_sentence,
                    "confidence": confidence,
                }

    def to_json_object(self) -> dict:
        return super().to_json_object() | {
            "endpoint": self.endpoint,
            "censor_token": self.censor_token,
            "confidence_cutoff": self.confidence_cutoff,
        }

    @classmethod
    def _get_constructor_kwargs(cls, obj):
        return super()._get_constructor_kwargs(obj) | {
            "endpoint": obj["endpoint"],
            "censor_token": obj["censor_token"],
            "confidence_cutoff": obj.get("confidence_cutoff", 0.40),
        }


@Rule.register_class
class ExternallyExecutedWordlistRule(OrderedWordlistRule):
    type_label = "external-wordlist"

    properties = RuleProperties(
        precedence=RulePrecedence.RIGHT,
        standalone=True,
    )

    def __init__(self,
                 dataset: str,
                 endpoint: str,
                 censor_token: str,
                 confidence_cutoff: float,
                 **super_kwargs):
        self.endpoint = endpoint
        self.censor_token = censor_token
        self.confidence_cutoff = confidence_cutoff
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
            if confidence >= self.confidence_cutoff:
                yield {
                    "match": self.censor_token,
                    "sensitivity": self.sensitivity.value if self.sensitivity else None,
                    "context": censored_sentence,
                    "confidence": confidence,
                }

    def to_json_object(self) -> dict:
        return super().to_json_object() | {
            "endpoint": self.endpoint,
            "censor_token": self.censor_token,
            "confidence_cutoff": self.confidence_cutoff,
        }

    @classmethod
    def _get_constructor_kwargs(cls, obj):
        return super()._get_constructor_kwargs(obj) | {
            "endpoint": obj["endpoint"],
            "censor_token": obj["censor_token"],
            "confidence_cutoff": obj.get("confidence_cutoff", 0.40),
        }
