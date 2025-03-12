import random
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from knowsys.tree._types import SpaceType, NodeType


class NodeList[T](list):

    def sample(self):
        return random.sample(self, 1)[0]

    def sample_with_children(self, include_self=False):
        if include_self is True:
            raise ValueError
        all_items = []
        def _travel_list(item: NodeType):
            all_items.append(item)
            for i in item.children:
                _travel_list(i)

        for item in self:
            _travel_list(item)
        return random.sample(all_items, 1)[0]
