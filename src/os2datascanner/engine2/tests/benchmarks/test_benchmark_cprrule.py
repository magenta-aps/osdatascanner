# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Benchmarking for CPRRule."""
from os2datascanner.engine2.rules.cpr import CPRRule
from .utilities import HTML_CONTENT


def test_benchmark_cpr_rule_no_context(benchmark):
    """Test performance on CPRRule without enabling examine_context."""
    content = HTML_CONTENT
    rule = CPRRule(modulus_11=True,
                   ignore_irrelevant=False,
                   examine_context=False)
    benchmark(rule.match, content)


def test_benchmark_cpr_rule_with_context(benchmark):
    """Test performance on CPRRule with examine_context enabled."""
    content = HTML_CONTENT
    rule = CPRRule(modulus_11=True,
                   ignore_irrelevant=False,
                   examine_context=True)
    benchmark(rule.match, content)
