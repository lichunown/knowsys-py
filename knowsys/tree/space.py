import random
from typing import *


if TYPE_CHECKING:
    from semantic_compare.tree._types import SpaceType, NodeType
    from semantic_compare.tree.node_list import NodeList


class TreeSpace(object):

    def __init__(self, name: str):
        self.name = name
        self.node_dict: Dict[str, NodeType]  = {}

        self._modify_flag = False
        self._del_nodes: Dict[str, NodeType]  = {}
        # space_collection.add(self)

    def delete(self, child):
        from semantic_compare.tree.node import TreeNode

        if isinstance(child, TreeNode):
            child = child.id_
        if child in self.node_dict:
            self._del_nodes[child] = self.node_dict[child]
            del self.node_dict[child]

    def delete_without_children(self, child):
        global_parent_id = child.parent_id if child.parent_id is not None else None
        for child_child in child.children:
            child_child.parent_id = global_parent_id
        self.delete(child)

    def delete_with_children(self, child):
        for child_child in child.children:
            self.delete_with_children(child_child)
        self.delete(child)

    def cached_tag(self):
        self._modify_flag = False

    @property
    def no_changed(self):
        return not self._modify_flag

    def __setitem__(self, key: str, value: "NodeType"):
        self._modify_flag = True
        self.node_dict[key] = value

    def __getitem__(self, item: str) -> "NodeType":
        return self.node_dict[item]

    def deepcopy(self) -> "TreeSpace":
        import copy
        return copy.deepcopy(self)

    def remove(self, id_):
        from semantic_compare.tree.node import TreeNode

        if isinstance(id_, TreeNode):
            id_ = id_.id_
        if id_ in self.node_dict:
            del self.node_dict[id_]

    def get_children_of_node(self, node_id) -> List["NodeType"]:
        return list(filter(lambda x: x.parent_id == node_id, self.node_dict.values()))

    def roots(self) -> "NodeList":
        from semantic_compare.tree.node_list import NodeList
        return NodeList(filter(lambda x: x.parent_id is None, self.node_dict.values()))

    def root(self) -> "NodeType":
        return self.roots()[0]

    def sample(self):
        return self[random.sample(list(self.node_dict.keys()), 1)[0]]

    def __repr__(self):
        return f'TreeSpace({self.name}): roots: {self.roots()}'




