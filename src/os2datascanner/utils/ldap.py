from typing import (
        Tuple, Union, Callable, Iterator, Optional, Sequence, NamedTuple,
        MutableSequence)


class RDN(NamedTuple):
    """A relative distinguished name, a key-value pair used to identify LDAP
    fragments.

    RDNs are almost always used as sequences."""
    key: str
    value: str

    def __str__(self):
        return f"{self.key}={self.value}"

    @staticmethod
    def make_sequence(*strings: str) -> Sequence['RDN']:
        return tuple(RDN(k, v)
                for k, v in (s.split("=", 1) for s in reversed(strings)))

    @staticmethod
    def make_string(rdns: Sequence['RDN']) -> str:
        return ",".join(str(l) for l in reversed(rdns))


class LDAPNode(NamedTuple):
    """A node in a X.500/LDAP-style directory. (This is not even slightly
    supposed to be a complete implementation of RFC 4512, but it's enough of
    one for OS2datascanner's purposes.)

    Nodes consist of three things: a label, which is a (possibly empty)
    tuple of relative distinguished names; a list of child nodes; and a
    dictionary of arbitrary properties."""
    label: Sequence[RDN]
    children: MutableSequence['LDAPNode']
    properties: dict

    @staticmethod
    def make(label, *children: 'LDAPNode', **properties) -> 'LDAPNode':
        """The recommended constructor for LDAPNode objects."""
        return LDAPNode(tuple(label), list(children), properties)

    def collapse(self) -> 'LDAPNode':
        """Returns a new simplified LDAP hierarchy: multiple nodes at the top
        with a single child will be reduced to a single node with a multi-part
        label. (Nodes with single children further down the hierarchy will
        remain unchanged.)"""
        if len(self.children) == 1:
            child = self.children[0]
            new_properties = self.properties
            new_properties.update(child.properties)
            return LDAPNode.make(
                    self.label + child.label,
                    *child.children, **new_properties).collapse()
        else:
            return self

    def __str__(self) -> str:
        return RDN.make_string(self.label)

    def __repr__(self) -> str:
        return str(self) + f" <{len(self.children)}>"

    def walk(self, *, _parents: Sequence[RDN] = ()) -> Iterator[
            Tuple[Sequence[RDN], 'LDAPNode']]:
        """Enumerates all LDAPNodes in this hierarchy in depth-first order,
        along with their full distinguished names."""
        yield (_parents + self.label, self)
        for k in self.children:
            yield from k.walk(_parents=_parents + self.label)

    def diff(self, other: 'LDAPNode') -> Iterator[
            Tuple[Sequence[RDN], Tuple['LDAPNode', 'LDAPNode']]]:
        """Computes the difference between this LDAPNode hierarchy and another
        one."""
        our_leaves = {k: v for k, v in self.walk() if not v.children}
        their_leaves = {k: v for k, v in other.walk() if not v.children}
        ours = our_leaves.keys()
        theirs = their_leaves.keys()

        yield from ((k, our_leaves[k], None) for k in ours - theirs)
        yield from ((k, our_leaves[k], their_leaves[k])
                for k in ours & theirs if our_leaves[k] != their_leaves[k])
        yield from ((k, None, their_leaves[k]) for k in theirs - ours)

    def print(self, *, _levels: int = 0):
        """Prints a summary of this LDAP node and its descendants to the
        console."""
        print("  " * _levels, RDN.make_string(self.label))
        for k, v in self.properties.items():
            print("  " * (_levels + 1), f"- {k}: {v}")
        for k in self.children:
            k.print(_levels=_levels + 1)

    @classmethod
    def from_iterator(
            cls,
            iterator: Iterator[dict],
            dn_selector: Callable[[dict], str]=
                    lambda item: item.get("distinguishedName")):
        """Builds an LDAPNode hierarchy from an iterator of dictionaries
        representing user objects and returns its root. The hierarchy will be
        constructed based on the users' distinguished names. For example, the
        input

        [
            {"distinguishedName": "CN=Enki,L=Eridu,L=Sumer"},
            {"distinguishedName": "CN=Ninhursag,L=Eridu,L=Sumer"},
            {"distinguishedName": "CN=Gilgamesh,L=Uruk,L=Sumer"},
        ]

        would produce the hierarchy

                              (root)
                                |
                             L=Sumer
                            /       \
                     L=Eridu         L=Uruk
                    /       \              \
        CN=Ninhursag         CN=Enki        CN=Gilgamesh

        The dn_selector function is used to select the field containing the
        distinguished name; if it returns None for an item, then that item will
        be skipped. Each input dictionary is copied as the properties of the
        resulting LDAP node."""
        root = LDAPNode.make(())

        # It'd be nice if Python's for loops just *supported* guard syntax...
        for item, name in (
                (i, n) for i, n in ((ri, dn_selector(ri)) for ri in iterator)
                if n is not None):
            name = RDN.make_sequence(*name.strip().split(","))

            node = root
            for idx in range(len(name)):
                label = (name[idx],)
                child = None
                for ch in node.children:
                    if ch.label == label:
                        child = ch
                        break
                else:
                    child = LDAPNode.make(label)
                    node.children.append(child)
                node = child

            node.properties.update(item)

        return root