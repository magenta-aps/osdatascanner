from dataclasses import dataclass
from typing import Iterator, List, Match, Optional, Tuple, Dict
import re
from functools import partial
from itertools import chain
from enum import Enum, unique
import structlog

from .rule import Rule, Sensitivity
from .regex import RegexRule
from .logical import oxford_comma
from .utilities.context import make_context, add_context_filter
from .utilities.cpr_probability import modulus11_check, CprProbabilityCalculator, cpr_bin_check
from .utilities.properties import RuleProperties, RulePrecedence

logger = structlog.get_logger("engine2")

cpr_regex = r"\b(\d{6})(?:[ \-/\.\t]|[ ]\-[ ])?(\d{4})\b"
calculator = CprProbabilityCalculator()


# Attempt to filter CPR number-like strings out of all contexts
add_context_filter(
        partial(
                re.compile(cpr_regex).sub,
                "XXXXXX-XXXX"))


# if the sourronding context contains some of these, we get suspicious.
# fmt: off
# check if these delimiters are balanced
_pre_delim = ("(", "[", "{", "<", )
_post_delim = (")", "]", "}", ">", )
# any of these symbols in the context result in probability=0
_operators = ("+", "-", )
_symbols = ("!", "#", "%", )
_all_symbols = _operators + _symbols
# fmt: on


@dataclass
class WordOrSymbol:
    """For future analysis, it is practical to know if a word or symbol was
    found in the context of a match. This class takes the tuple from the regex
    findall method as an argument, and remembers whether it is a word or a
    symbol. Crucially, this allows us to remember the order of words and
    symbols in the context."""

    word: str | None
    symbol: str | None


@unique
class Context(Enum):
    WHITELIST = 1
    UNBALANCED = 2
    WRONG_CASE = 3
    NUMBER = 4
    SYMBOL = 5
    BLACKLIST = 6
    PROBABILITY_CALC = 7

    # XXX custom formatter, like __str__ or __format__(self, format_spec), for
    # printing only the enum name would be nice.


class CPRRule(RegexRule):
    type_label = "cpr"
    WHITELIST_WORDS = {"cpr", }
    BLACKLIST_WORDS = {
        "p-nr", r"p\.nr", "p-nummer", "pnr",
        "customer no", "customer-no",
        "bilagsnummer",
        "order number", "ordrenummer",
        "fakturanummer", "faknr", "fak-nr",
        "tullstatistisk", "tullstatistik",
        "test report no",
        r"protocol no\.",
        "dhk:tx",
    }
    properties = RuleProperties(
        precedence=RulePrecedence.LEFT,
        standalone=True)

    def __init__(self,
                 modulus_11: bool = True,
                 ignore_irrelevant: bool = True,
                 examine_context: bool = True,
                 whitelist: Optional[List[str]] = None,
                 blacklist: Optional[List[str]] = None,
                 exceptions: Optional[List[str]] = None,
                 surrounding_exceptions: Optional[List[str]] = None,
                 **super_kwargs):
        super().__init__(cpr_regex, **super_kwargs)
        self._modulus_11 = modulus_11
        self._ignore_irrelevant = ignore_irrelevant
        self._examine_context = examine_context
        self._whitelist = self.WHITELIST_WORDS if whitelist is None else set(whitelist)
        self._blacklist = self.BLACKLIST_WORDS if blacklist is None else set(blacklist)
        self._exceptions = frozenset(exceptions) if exceptions else frozenset()
        self._surrounding_exceptions = frozenset(
            surrounding_exceptions) if surrounding_exceptions else frozenset()
        self._blacklist_pattern = re.compile("|".join(self._blacklist))

    @property
    def presentation_raw(self) -> str:
        properties = []
        if self._modulus_11:
            properties.append("modulus 11")
        if self._ignore_irrelevant:
            properties.append("relevance check")
        if self._examine_context:
            properties.append("context check")

        if properties:
            return "CPR number (with {0})".format(oxford_comma(properties, "and"))
        else:
            return "CPR number"

    def match(self, content: str) -> Optional[Iterator[dict]]:  # noqa: CCR001,E501,C901 too high cognitive complexity
        if content is None:
            return

        if self._examine_context and self._blacklist:
            if (m := self._blacklist_pattern.search(content.lower())):
                logger.debug("Blacklist matched content", matches=m.group(0))
                return

        def _probability(match: Match[str]):
            """Given a match, calculates probability of being a cpr number,
             by using the relevant probability calculations."""
            cpr = match_to_cpr(match)

            probability = 1.0
            if self._ignore_irrelevant:
                probability = calculator.cpr_check(cpr, do_mod11_check=False)
                if isinstance(probability, str):
                    logger.debug(f"{cpr} is not valid cpr due to {probability}")
                    return False

            cpr = cpr[0:4] + "XXXXXX"
            low, high = match.span()
            # only examine context if there is any
            if self._examine_context and len(content) > (high - low):
                p, ctype = self.examine_context(match)
                # determine if probability stems from context or calculator
                probability = p if p is not None else probability
                ctype = ctype if ctype != [] else Context.PROBABILITY_CALC
                logger.debug(f"{cpr} with probability {probability} from context "
                             f"due to {ctype}")

            return probability

        def _is_cpr(candidate: Match[str]):
            """Given a match, checks expections, modulus 11 check and calculates probability,
             to determine if it is a cpr number."""
            cpr = match_to_cpr(candidate)

            if cpr in self._exceptions:
                return False

            if self._modulus_11:
                mod11, reason = modulus11_check(cpr)
                if not mod11:
                    logger.debug(f"{cpr} failed modulus11 check due to {reason}")
                    return False

            return True if _probability(candidate) else False

        numbers = [m for m in self._compiled_expression.finditer(content)]

        cpr_numbers = [m for m in numbers if _is_cpr(m)]

        if self._examine_context:
            cpr_numbers = cpr_bin_check(numbers, cpr_numbers)

        for m in cpr_numbers:
            cpr = match_to_cpr(m)
            cpr = cpr[0:4] + "XXXXXX"

            yield {
                "match": cpr,

                **make_context(m, content),

                "sensitivity": (
                    self.sensitivity.value if self.sensitivity
                    else self.sensitivity
                ),
                "probability": _probability(m),
            }

    def examine_context(  # noqa: CCR001, C901 too high cognitive complexity
        self, match: Match[str]
    ) -> Tuple[Optional[float], List[tuple]]:
        """Estimate a probality (0-1) based on the context of the match

        Returns 0.0 if any of the following conditions are found
        - There are unmatched delimiters, like () or {}
        - The CPR-nr is surrounded by a number that doesn't resembles a CPR
        - The word before or after is not either: lower-, title- or upper-case.
        - A blacklisted surrounding_exception word is found around a CPR match

        But returns 1.0 if
        - pre-context contains "cpr" or any other whitelist words
        """

        probability = None
        words_or_syms = self.extract_surrounding_words(match, n_words=3)
        ctype = []

        # test if a whitelist- or surrounding_exception -string is found in the context words.
        # combine the list of 'pre' & 'post' keys in words dict.
        words_lower = [
            w.word.lower() for w in chain.from_iterable(
                words_or_syms.values()) if w.word]
        if self._whitelist:
            for w in self._whitelist:
                for cw in words_lower:
                    if w in cw:
                        ctype.append((Context.WHITELIST, cw))
                        return 1.0, ctype
        if self._surrounding_exceptions:
            for cw in words_lower:
                if cw in self._surrounding_exceptions:
                    ctype.append((Context.BLACKLIST, cw))
                    return 0.0, ctype

        # test for balanced delimiters
        # XXX: This only checks number of delimiters, not type, so. "[111111-1118}" is accepted
        delimiters = 0
        for w in chain.from_iterable(words_or_syms.values()):
            if not w.symbol:
                continue
            w = w.symbol
            if w in _pre_delim:
                delimiters += 1
            elif w in _post_delim:
                delimiters -= 1
            elif w in _all_symbols:
                ctype.append((Context.SYMBOL, w))
                probability = 0.0
        if delimiters != 0:
            ctype.append((Context.UNBALANCED, delimiters))
            probability = 0.0

        # only do context checking on surrounding words
        for w in [words_or_syms["pre"][-1], words_or_syms["post"][0]]:
            if not w.word or self._compiled_expression.match(w.word):
                continue
            # test if surrounding word is a number (and not looks like a cpr)
            elif w.word and is_number(w.word):
                probability = 0.0
                ctype.append((Context.NUMBER, w.word))
            elif w.word and not is_alpha_case(w.word):
                # test for case, ie Magenta, magenta, MAGENTA are ok, but not MaGenTa
                # nor magenta10. w must not be empty string
                probability = 0.0
                ctype.append((Context.WRONG_CASE, w.word))

        return probability, ctype

    def extract_surrounding_words(
        self, match: Match[str], n_words: int = 2
    ) -> Tuple[Dict[str, list], Dict[str, list]]:
        """Extract at most `n_words` before and after the match

        Return a dict with words and one with symbols
        """

        # get full content
        content = match.string
        low, high = match.span()
        # get previous/next n words
        pre = " ".join(content[max(low-50, 0):low].split()[-n_words:])
        post = " ".join(content[high:high+50].split()[:n_words])

        word_regex = r"(\w+(?:[-\./]\w*)*)"
        symbol_regex = r"([^\w\s\.\"])"
        # split in two capture groups: (word, symbol)
        # Ex: 'The brown, fox' ->
        # [('The', ''), ('brown', ''), ('', ','), ('fox', '')]
        split_str = r"|".join([word_regex, symbol_regex])
        pre_res = re.findall(split_str, pre)
        post_res = re.findall(split_str, post)
        # remove empty strings
        pre_words = [WordOrSymbol(*s) for s in pre_res]
        post_words = [WordOrSymbol(*s) for s in post_res]

        # XXX Should be set instead?
        words_or_syms = dict(
            pre=pre_words if len(pre_words) > 0 else [WordOrSymbol("", "")],
            post=post_words if len(post_words) > 0 else [WordOrSymbol("", "")],
        )

        return words_or_syms

    def to_json_object(self) -> dict:
        # Deliberately skip the RegexRule implementation of this method (we
        # don't need to include our expression, as it's static)
        return dict(
            **super(RegexRule, self).to_json_object(),
            modulus_11=self._modulus_11,
            ignore_irrelevant=self._ignore_irrelevant,
            examine_context=self._examine_context,
            whitelist=list(self._whitelist),
            blacklist=list(self._blacklist),
            exceptions=",".join(self._exceptions),
            surrounding_exceptions=",".join(self._surrounding_exceptions)
        )

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj: dict):
        # For backwards compatibility, we also need to handle whitelist and
        # blacklist fields consisting of booleans
        whitelist = obj.get("whitelist", None)
        blacklist = obj.get("blacklist", None)
        if whitelist is True:  # use the default whitelist
            whitelist = None
        elif whitelist is False:  # don't use a whitelist at all
            whitelist = ()
        if blacklist is True:
            blacklist = None
        elif blacklist is False:
            blacklist = ()

        return CPRRule(
            modulus_11=obj.get(
                "modulus_11",
                True),
            ignore_irrelevant=obj.get(
                "ignore_irrelevant",
                True),
            examine_context=obj.get(
                "examine_context",
                True),
            sensitivity=Sensitivity.make_from_dict(obj),
            name=obj.get("name"),
            whitelist=whitelist,
            blacklist=blacklist,
            # Sometimes, for whatever reason, a list is passed here instead of
            # a comma-separated string. A TODO would be to figure out why.
            exceptions=obj.get("exceptions").split(",") if isinstance(
                    obj.get("exceptions"), str)
            else obj.get("exceptions"),
            surrounding_exceptions=obj.get("surrounding_exceptions").split(",") if isinstance(
                    obj.get("surrounding_exceptions"), str)
            else obj.get("surrounding_exceptions"))


def is_number(s: str) -> bool:
    """Return True if the string is a int/float"""

    # this is the faster than try: float or re.match
    # https://stackoverflow.com/a/23639915
    return s.replace(".", "", 1).replace(",", "", 1).isdigit()


def is_alpha_case(s: str) -> bool:
    """Return True for Magenta, magenta, MAGENTA but not MaGenTa"""

    # make sure words with hypen are accepted as long as the case is ok
    s = s.replace("-", "")
    # We could enforce s.isalpha() to prevent ma10ta, but then "nr:" would fail
    return s.istitle() or s.islower() or s.isupper()  # and s.isalpha()


def match_to_cpr(match: Match[str]):
    """Converts a match object into a cpr number without hyphen or space."""
    return match.group(1).replace(" ", "") + match.group(2)
