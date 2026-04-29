import random
from typing import TYPE_CHECKING, Callable, List, Optional

if TYPE_CHECKING:
    from knowsys.tree._types import SpaceType, NodeType


class NodeList(list):

    def sample(self):
        return random.sample(self, 1)[0]

    def sample_k(self, k):
        if len(self) <= k:
            return self
        return random.sample(self, k)

    def sample_with_children(self, include_self=False):
        if include_self:
            raise ValueError
        all_items = []
        def _travel_list(item: NodeType):
            all_items.append(item)
            for i in item.children:
                _travel_list(i)

        for item in self:
            _travel_list(item)
        return random.sample(all_items, 1)[0]

    def filter(self, func: "Callable[[NodeType], bool]") -> "NodeList":
        return NodeList(filter(func, self))

    def get_by_name_all(self, name) -> List[Optional["NodeType"]]:
        return self.filter(lambda x: x.name == name)

    def get_by_name(self, name) -> Optional["NodeType"]:
        return self.filter(lambda x: x.name == name)[0]

    def __contains__(self, item):
        if isinstance(item, str):
            return item in [i.name for i in self]
        return super().__contains__(item)
