from ..rule import Rule, SimpleRule
from ..logical import CompoundRule, NotRule, OrRule, AndRule


def optimize_rule(rule: Rule):
    """
    Uses rules of inference to the extend possible to
    eliminate logical connectives (compound rules) for
    a given rule, i.e. for a rule: "Not(Not(R))" it
    eliminates the double negation and returns the rule "R".
    """
    match rule:
        case NotRule(_rule=NotRule(_rule=inner_rule)):
            return optimize_rule(inner_rule)
        case CompoundRule() | OrRule() | AndRule():
            return rule.__class__(*[optimize_rule(r) for r in rule._components])
        case SimpleRule():
            return rule
