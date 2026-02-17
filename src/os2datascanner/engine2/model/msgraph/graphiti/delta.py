# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from .baseclasses import AbstractGraphNode, EndpointNode


class GraphDeltaNode(EndpointNode):
    """
    Graph Node for the '/delta' endpoint.
    """

    def __init__(self, parent: AbstractGraphNode):
        self._parent = parent

    def build(self) -> str:
        return self.parent().build() + '/delta'

    def parent(self) -> AbstractGraphNode:
        return self._parent
