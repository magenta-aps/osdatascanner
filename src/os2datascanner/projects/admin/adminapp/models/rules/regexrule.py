# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2Webscanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (http://www.os2web.dk/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( http://www.os2web.dk/ )

from django.db import models


from os2datascanner.engine2.rules.regex import RegexRule as RegexTwule
from .rule import Rule


class RegexRule(Rule):
    """Represents matching rules based on regular expressions."""

    def make_engine2_rule(self) -> RegexTwule:
        # Use the original engine's RegexRule abstraction to make the required
        # compound expression
        return RegexTwule(
                compund_rules(self),
                sensitivity=self.make_engine2_sensitivity(),
                name=self.name)


class RegexPattern(models.Model):
    """
    Represents a regular expression pattern to be added to a RegexRule.
    """

    regex = models.ForeignKey(RegexRule, null=True, on_delete=models.CASCADE,
                              related_name='patterns', verbose_name='Regex')

    pattern_string = models.CharField(max_length=1024, blank=False,
                                      verbose_name='Udtryk')

    def __str__(self):
        """Return the pattern string."""
        return self.pattern_string

    class Meta:
        verbose_name = 'Pattern'
        ordering = ('pk',)


def compund_rules(rule):
    """
    This method compounds all the regex patterns in the rule set into one regex rule that is OR'ed
    e.g. A ruleSet of {pattern1, pattern2, pattern3} becomes (pattern1 | pattern2 | pattern3)
    :return: RegexRule representing the compound rule
    """

    rule_set = set(rule.patterns.all())
    if len(rule_set) == 1:
        return rule_set.pop().pattern_string
    if len(rule_set) > 1:
        compound_rule = '('
        for _ in rule.patterns.all():
            compound_rule += rule_set.pop().pattern_string
            if not rule_set:
                compound_rule += ')'
            else:
                compound_rule += '|'
        return compound_rule
    if len(rule_set) < 1:
        return None
