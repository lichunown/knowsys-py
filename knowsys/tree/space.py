import functools
import random
from typing import *

from knowsys.tree.cacheing import OutCacheMixin, OutCacheWrapper

if TYPE_CHECKING:
    from knowsys.tree._types import SpaceType, NodeType, Relation, Entity, RelationTerm, EntityTerm, AttributeTerm, Attribute, ERTerm
    from knowsys.tree.node_list import NodeList


class TreeSpace(OutCacheMixin):

    _cache_wrapper = OutCacheWrapper()

    def __init__(self, name: str):
        self.name = name
        self.node_dict: Dict[str, NodeType]  = {}
        self._del_nodes: Dict[str, NodeType]  = {}

    def delete(self, child):
        from knowsys.tree.node import TreeNode
        if isinstance(child, TreeNode):
            child = child.id_
        if child in self.node_dict:
            self._del_nodes[child] = self.node_dict[child]
            del self.node_dict[child]
            self.modifying((child.__class__.__name__, 'all'))

    def delete_without_children(self, child):
        global_parent_id = child.parent_id if child.parent_id is not None else None
        for child_child in child.children:
            child_child.parent_id = global_parent_id
        self.delete(child)

    def delete_with_children(self, child):
        for child_child in child.children:
            self.delete_with_children(child_child)
        self.delete(child)

    def lazy_check(self):
        for node in self.node_dict.values():
            node.lazy_check()

    def __contains__(self, item):
        from knowsys.tree.node import TreeNode
        if isinstance(item, TreeNode):
            item = item.id_
        return item in self.node_dict

    def __setitem__(self, key: str, value: "NodeType"):
        self.node_dict[key] = value
        self.modifying((value.__class__.__name__, 'all'))

    def __getitem__(self, item: str) -> "NodeType":
        return self.node_dict[item]

    def deepcopy(self) -> "TreeSpace":
        import copy
        return copy.deepcopy(self)

    def filter(self, func: "Callable[[NodeType], bool]") -> "NodeList[NodeType]":
        from knowsys.tree.node_list import NodeList
        return NodeList(filter(func, self.node_dict.values()))

    @_cache_wrapper.cache('all')
    def get_by_name(self, name) -> Optional["NodeType"]:
        res = self.filter(lambda x: x.name == name)
        return None if len(res) == 0 else res[0]

    @_cache_wrapper.cache('all')
    def get_children_of_node(self, node_id) -> List["NodeType"]:
        return self.filter(lambda x: x.parent_id == node_id)

    @_cache_wrapper.cache('all')
    def roots(self) -> "NodeList":
        return self.filter(lambda x: x.parent_id is None)

    def __repr__(self):
        return f'TreeSpace({self.name})'

    @property
    @_cache_wrapper.cache('all', 'Relation')
    def relation_root(self) -> "Relation":
        from knowsys.types import Relation
        return self.filter(lambda x: x.parent is None and isinstance(x, Relation))[0]

    @property
    @_cache_wrapper.cache('all', 'Entity')
    def entity_root(self) -> "Entity":
        from knowsys.types import Entity
        return self.filter(lambda x: x.parent is None and isinstance(x, Entity))[0]

    @property
    @_cache_wrapper.cache('all', 'EntityTerm')
    def entity_term_root(self) -> "EntityTerm":
        from knowsys.types import EntityTerm
        return self.filter(lambda x: x.parent is None and isinstance(x, EntityTerm))[0]

    @property
    @_cache_wrapper.cache('all', 'RelationTerm')
    def relation_term_root(self) -> "RelationTerm":
        from knowsys.types import RelationTerm
        return self.filter(lambda x: x.parent is None and isinstance(x, RelationTerm))[0]

    @property
    @_cache_wrapper.cache('all', 'ERTerm')
    def er_term_root(self) -> "ERTerm":
        from knowsys.types import ERTerm
        return self.filter(lambda x: x.parent is None and isinstance(x, ERTerm))[0]

    @property
    @_cache_wrapper.cache('all', 'Attribute')
    def attribute_root(self) -> "Attribute":
        from knowsys.types import Attribute
        return self.filter(lambda x: x.parent is None and isinstance(x, Attribute))[0]

    @property
    @_cache_wrapper.cache('all', 'AttributeTerm')
    def attribute_term_root(self) -> "AttributeTerm":
        from knowsys.types import AttributeTerm
        return self.filter(lambda x: x.parent is None and isinstance(x, AttributeTerm))[0]

    @_cache_wrapper.cache('all', 'RelationTerm')
    def relation_terms_of_relation_all(self, relation: "Relation") -> List["RelationTerm"]:
        from knowsys.types import RelationTerm
        return self.filter(lambda x: isinstance(x, RelationTerm) and x.relation_id == relation.id_)

    @_cache_wrapper.cache('all', 'EntityTerm')
    def entity_terms_of_entity_all(self, entity: "Entity") -> List["EntityTerm"]:
        from knowsys.types import EntityTerm
        return self.filter(lambda x: isinstance(x, EntityTerm) and x.entity_id == entity.id_)

    @_cache_wrapper.cache('all', 'ERTerm')
    def er_terms_of_relation_term_all(self, relation_term: "RelationTerm") -> List["ERTerm"]:
        from knowsys.types import ERTerm
        return self.filter(lambda x: isinstance(x, ERTerm) and x.relation_term_id == relation_term.id_)

    @_cache_wrapper.cache('all', 'RelationTerm')
    def relation_terms_of_relation_root(self, relation: "Relation") -> List["RelationTerm"]:
        from knowsys.types import RelationTerm
        return self.filter(lambda x: isinstance(x, RelationTerm) and x.relation_id == relation.id_ and x.parent is not None and x.parent == self.relation_term_root)

    @_cache_wrapper.cache('all', 'EntityTerm')
    def entity_terms_of_entity_root(self, entity: "Entity") -> List["EntityTerm"]:
        from knowsys.types import EntityTerm
        return self.filter(lambda x: isinstance(x, EntityTerm) and x.entity_id == entity.id_ and x.level == 1)

    @_cache_wrapper.cache('all', 'ERTerm')
    def er_terms_of_relation_term_root(self, relation_term: "RelationTerm") -> List["ERTerm"]:
        from knowsys.types import ERTerm
        return self.filter(lambda x: isinstance(x, ERTerm) and x.relation_term_id == relation_term.id_ and x.parent is not None and x.parent == self.er_term_root)

    @_cache_wrapper.cache('all', 'Attribute')
    def attributes_of_node_all(self, entity: Union["Entity", "Relation"]):
        from knowsys.types import Attribute
        return self.filter(lambda x: isinstance(x, Attribute) and x.modify_id == entity.id_)

    @_cache_wrapper.cache('all', 'Attribute')
    def attributes_of_node_root(self, entity: Union["Entity", "Relation"]):
        from knowsys.types import Attribute
        return self.filter(lambda x: isinstance(x, Attribute) and x.modify_id == entity.id_ and x.level == 2)

    @_cache_wrapper.cache('all', 'AttributeTerm')
    def attribute_term_of_node_all(self, item: Union["Entity", "Relation", "Attribute"]):
        from knowsys.types import AttributeTerm
        return self.filter(lambda x: isinstance(x, AttributeTerm) and (x.modify_id == item.id_ or x.attribute_id == item.id_))

    @_cache_wrapper.cache('all', 'AttributeTerm')
    def attribute_term_of_node_root(self, item: Union["Entity", "Relation", "Attribute"]):
        from knowsys.types import AttributeTerm
        return self.filter(lambda x: isinstance(x, AttributeTerm) and (x.modify_id == item.id_ or x.attribute_id == item.id_) and x.level == 1)


if __name__ == '__main__':
    pass
    # from knowsys.tree.node import TreeNode
    # space = TreeSpace('_')
    # root = TreeNode(None, 'root', None, space)
    # root.create_child('a')
    # root.create_child('b')
    # space.re_cacheing()
    #
