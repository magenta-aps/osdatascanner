# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""
"""

from .baseclasses import AbstractGraphNode, EndpointNode


class GraphExtensionsNode(EndpointNode):
    """
    Graph Node for the '/extensions' endpoint
    """

    def __init__(self, parent: AbstractGraphNode, eid=None):
        self._parent = parent
        self._eid = eid

    def build(self) -> str:
        url = (f'/extensions/{self._eid}' if self._eid
               else '/extensions')
        return self.parent().build() + url

    def parent(self) -> AbstractGraphNode:
        return self._parent
