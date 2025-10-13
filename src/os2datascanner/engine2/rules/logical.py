from abc import abstractmethod
from typing import Sequence
from functools import reduce
from .rule import Rule, Sensitivity


def oxford_comma(parts: Sequence, conjunction: str, *, key=lambda c: str(c)) -> str:
    """Join a list-like using oxford comma, ie. comma before the conjuction term

    Example with `and` as the conjuction
    To my parents, Ayn Rand and God.  (withot oxford)
    To my parents, Ayn Rand, and God. (with oxford)

    """
    if len(parts) == 0:
        raise ValueError("Can't combine empty list of words")
    elif len(parts) == 1:
        return key(parts[0])
    else:
        start = [key(p) for p in parts[0:-1]]
        end = key(parts[-1])
        if len(start) == 1:
            return "{0} {1} {2}".format(start[0], conjunction, end)
        else:
            return "{0}, {1} {2}".format(", ".join(start), conjunction, end)


class CompoundRule(Rule):
    def __init__(self, *components, **super_kwargs):
        super().__init__(**super_kwargs)
        if len(components) == 0:
            raise ValueError("CompoundRule with zero components")
        self._components = components

    @property
    def components(self) -> list[Rule]:
        return self._components

    # It might have been nice to have a special implementation of
    # Rule.sensitivity here that finds the component with the highest
    # sensitivity and returns that, but that doesn't actually make sense: the
    # sensitivity of a CompoundRule is a function of the *matched* components,
    # not of all components considered out of context

    @classmethod
    @abstractmethod
    def make(cls, *components):
        """Creates a new Rule that represents the combination of all of the
        given components. The result does not need to be an instance of @cls:
        it could be a completely different kind of Rule, or a simple boolean
        value, if this rule can already be reduced to one.

        Subclasses must override this method, but should call up to this
        implementation."""
        if len(components) == 0:
            raise ValueError("CompoundRule with zero components")
        elif len(components) == 1:
            return components[0]
        else:
            args = []
            for k in components:
                if isinstance(k, cls):
                    args.extend(k._components)
                else:
                    args.append(k)
            return cls(*args)

    def split(self):
        match self._components:
            case [head]:
                # Trivial case: just defer to the only component
                return head.split()
            case [head, *tail]:
                next_rule, pve, nve = head.split()
                return next_rule, self.make(pve, *tail), self.make(nve, *tail)
            case _:
                raise ValueError

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            components=[c.to_json_object() for c in self._components],
        )

    def flatten(self):
        return reduce(lambda set_, component: set_ | component.flatten(), self._components, set())


class AllRule(CompoundRule):
    """An AllRule is a CompoundRule which always evaluates all of its
    components -- that is, it has no short-circuiting. (This is useful when you
    really do want the engine to perform multiple checks at once.)

    The final positive continuation of an AllRule will be True if any of its
    components matched, and False otherwise."""
    type_label = "all"

    def __init__(self, *components, satisfied: bool = False, **super_kwargs):
        super().__init__(*components, **super_kwargs)
        self._satisfied = satisfied

    @property
    def presentation_raw(self):
        if len(self._components) == 0:
            return "Empty AllRule"
        elif len(self._components) < 3:
            return "({0})".format(oxford_comma(self._components, "or"))
        else:
            return "({0})".format(oxford_comma(self._components, "or any of"))

    @classmethod
    def make(cls, *components, satisfied: bool = False):
        if len(components) == 1:
            return components[0]

        new_components = []
        for k in components:
            if k is True:
                satisfied = True
            elif k is not False:
                new_components.append(k)
        return (AllRule(*new_components, satisfied=satisfied)
                if new_components else satisfied)

    def split(self):
        fst, rest = self._components[0], self._components[1:]
        return fst, self.make(*rest, True), self.make(*rest, self._satisfied)

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            satisfied=self._satisfied
        )

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj):
        return AllRule(
            *[Rule.from_json_object(o) for o in obj["components"]],
            sensitivity=Sensitivity.make_from_dict(obj),
            name=obj["name"] if "name" in obj else None,
            satisfied=obj.get("satisfied", False)
        )


class AndRule(CompoundRule):
    """An AndRule is a CompoundRule corresponding to the C "&&" operator or the
    Python "and" operator (i.e., it has short-circuiting: as soon as one
    component reduces to False, no other components will be evaluated)."""

    type_label = "and"

    @property
    def presentation_raw(self):
        return "({0})".format(oxford_comma(self._components, "and"))

    @classmethod
    def make(cls, *components):
        if False in components:
            return False
        else:
            return super().make(*[c for c in components if c is not True])

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj):
        return AndRule(
            *[Rule.from_json_object(o) for o in obj["components"]],
            sensitivity=Sensitivity.make_from_dict(obj),
            name=obj["name"] if "name" in obj else None,
        )


class OrRule(CompoundRule):
    """An OrRule is a CompoundRule corresponding to the C "||" operator or the
    Python "or" operator (i.e., it has short-circuiting: as soon as one
    component reduces to True, no other components will be evaluated)."""

    type_label = "or"

    @property
    def presentation_raw(self):
        return "({0})".format(oxford_comma(self._components, "or"))

    @classmethod
    def make(cls, *components):
        if True in components:
            return True
        else:
            return super().make(*[c for c in components if c is not False])

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj):
        return OrRule(
            *[Rule.from_json_object(o) for o in obj["components"]],
            sensitivity=Sensitivity.make_from_dict(obj),
            name=obj["name"] if "name" in obj else None,
        )


class NotRule(Rule):
    """An NotRule is a negation rule, working on another @rule.

    Splitting it, returns the negate of @pve and @nve from @rule. I.e. if @pve of
    @rule is False, then NotRule(@rule).split() returns @pve=True
    """
    type_label = "not"

    def __init__(self, rule, **super_kwargs):
        super().__init__(**super_kwargs)
        if not rule:
            raise ValueError("Couldn't construct NotRule: No rule given")
        self._rule = rule

    @property
    def presentation_raw(self):
        return "not {0}".format(self._rule.presentation)

    @staticmethod
    def make(component):
        if component is True:
            return False
        elif component is False:
            return True
        elif isinstance(component, NotRule):
            return component._rule
        else:
            return NotRule(component)

    def split(self):
        rule, pve, nve = self._rule.split()
        return rule, self.make(pve), self.make(nve)

    def to_json_object(self):
        return dict(**super().to_json_object(), rule=self._rule.to_json_object())

    def flatten(self):
        return self._rule.flatten()

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj):
        return NotRule(
            Rule.from_json_object(obj["rule"]),
            sensitivity=Sensitivity.make_from_dict(obj),
            name=obj["name"] if "name" in obj else None,
        )


def make_if(predicate, then, else_):
    return OrRule.make(
        AndRule.make(predicate, then),
        AndRule.make(NotRule.make(predicate), else_),
    )
