from collections import defaultdict
from typing import *

if TYPE_CHECKING:
    from knowsys.tree._types import SpaceType, NodeType, Relation, Entity, RelationTerm, EntityTerm, AttributeTerm, Attribute, ERTerm
    from knowsys.tree.node_list import NodeList


class TreeSpace:

    def __init__(self, name: str):
        self.name = name
        self.node_dict: Dict[str, NodeType]  = {}
        self._del_nodes: Dict[str, NodeType]  = {}
        self._init_indexes()

    def _init_indexes(self):
        self._name_index: Dict[str, List["NodeType"]] = defaultdict(list)
        self._children_by_parent: Dict[Optional[str], List["NodeType"]] = defaultdict(list)
        self._type_index: Dict[str, List["NodeType"]] = defaultdict(list)
        self._attributes_by_modify: Dict[str, List["NodeType"]] = defaultdict(list)
        self._attribute_terms_by_attribute: Dict[str, List["NodeType"]] = defaultdict(list)
        self._attribute_terms_by_modify: Dict[str, List["NodeType"]] = defaultdict(list)
        self._relation_terms_by_relation: Dict[str, List["NodeType"]] = defaultdict(list)
        self._relation_terms_by_from_entity: Dict[str, List["NodeType"]] = defaultdict(list)
        self._relation_terms_by_to_entity: Dict[str, List["NodeType"]] = defaultdict(list)
        self._entity_terms_by_entity: Dict[str, List["NodeType"]] = defaultdict(list)
        self._er_terms_by_relation_term: Dict[str, List["NodeType"]] = defaultdict(list)

    def _index_node(self, node: "NodeType"):
        """Update lookup indexes for one node.

        The space is optimized around read-heavy graph queries.  Maintaining
        these indexes makes common lookups proportional to the result size
        instead of scanning every node in the knowledge system.
        """
        self._name_index[node.name].append(node)
        self._children_by_parent[node.parent_id].append(node)

        class_names = [cls.__name__ for cls in node.__class__.mro()]
        for class_name in class_names:
            self._type_index[class_name].append(node)

        if node.__class__.__name__ == "Attribute":
            modify_id = getattr(node, "modify_id", None)
            if modify_id is not None:
                self._attributes_by_modify[modify_id].append(node)
        elif node.__class__.__name__ == "AttributeTerm":
            attribute_id = getattr(node, "attribute_id", None)
            modify_id = getattr(node, "modify_id", None)
            if attribute_id is not None:
                self._attribute_terms_by_attribute[attribute_id].append(node)
            if modify_id is not None:
                self._attribute_terms_by_modify[modify_id].append(node)
        elif node.__class__.__name__ == "RelationTerm":
            relation_id = getattr(node, "relation_id", None)
            if relation_id is not None:
                self._relation_terms_by_relation[relation_id].append(node)
                try:
                    self._relation_terms_by_from_entity[node.from_entity.id_].append(node)
                    self._relation_terms_by_to_entity[node.to_entity.id_].append(node)
                except Exception:
                    # The relation may not be ready until lazy inheritance has
                    # finished.  lazy_check() rebuilds indexes after that pass.
                    pass
        elif node.__class__.__name__ == "EntityTerm":
            entity_id = getattr(node, "entity_id", None)
            if entity_id is not None:
                self._entity_terms_by_entity[entity_id].append(node)
        elif node.__class__.__name__ == "ERTerm":
            relation_term_id = getattr(node, "relation_term_id", None)
            if relation_term_id is not None:
                self._er_terms_by_relation_term[relation_term_id].append(node)

    def rebuild_indexes(self):
        """Rebuild all indexes from the current node state.

        Some node fields are inherited during lazy validation, and a few
        maintenance operations update parent ids in place.  Rebuilding after
        those operations keeps the indexes simple and avoids stale query data.
        """
        self._init_indexes()
        for node in self.node_dict.values():
            self._index_node(node)

    def _as_node_list(self, nodes: Iterable["NodeType"]) -> "NodeList":
        from knowsys.tree.node_list import NodeList
        return NodeList(nodes)

    def _nodes_of_type(self, class_name: str) -> "NodeList":
        return self._as_node_list(self._type_index.get(class_name, []))

    def delete(self, child):
        from knowsys.tree.node import TreeNode
        if isinstance(child, TreeNode):
            child = child.id_
        if child in self.node_dict:
            self._del_nodes[child] = self.node_dict[child]
            del self.node_dict[child]
            self.rebuild_indexes()

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
        self.rebuild_indexes()

    def __contains__(self, item):
        from knowsys.tree.node import TreeNode
        if isinstance(item, TreeNode):
            item = item.id_
        return item in self.node_dict

    def __setitem__(self, key: str, value: "NodeType"):
        if key in self.node_dict:
            self.node_dict[key] = value
            self.rebuild_indexes()
            return
        self.node_dict[key] = value
        self._index_node(value)

    def __getitem__(self, item: str) -> "NodeType":
        return self.node_dict[item]

    def deepcopy(self) -> "TreeSpace":
        import copy
        return copy.deepcopy(self)

    def filter(self, func: "Callable[[NodeType], bool]") -> "NodeList[NodeType]":
        from knowsys.tree.node_list import NodeList
        return NodeList(filter(func, self.node_dict.values()))

    def get_by_name_all(self, name) -> List[Optional["NodeType"]]:
        return self._as_node_list(self._name_index.get(name, []))

    def get_by_name(self, name) -> Optional["NodeType"]:
        res = self.get_by_name_all(name)
        return None if len(res) == 0 else res[0]

    def get_children_of_node(self, node_id) -> List["NodeType"]:
        return self._as_node_list(self._children_by_parent.get(node_id, []))

    def roots(self) -> "NodeList":
        return self._as_node_list(self._children_by_parent.get(None, []))

    def __repr__(self):
        return f'TreeSpace({self.name})'

    @property
    def root(self):
        return self.node_dict['1011000000000006']

    @property
    def relation_root(self) -> "Relation":
        return self._nodes_of_type("Relation").filter(lambda x: x.parent_id == self.root.id_)[0]

    @property
    def entity_root(self) -> "Entity":
        return self._nodes_of_type("Entity").filter(lambda x: x.parent_id == self.root.id_)[0]

    @property
    def entity_term_root(self) -> "EntityTerm":
        return self._nodes_of_type("EntityTerm").filter(lambda x: x.parent_id is None)[0]

    @property
    def relation_term_root(self) -> "RelationTerm":
        return self._nodes_of_type("RelationTerm").filter(lambda x: x.parent_id is None)[0]

    @property
    def er_term_root(self) -> "ERTerm":
        return self._nodes_of_type("ERTerm").filter(lambda x: x.parent_id is None)[0]

    @property
    def attribute_root(self) -> "Attribute":
        return self._nodes_of_type("Attribute").filter(lambda x: x.parent_id is None)[0]

    @property
    def attribute_term_root(self) -> "AttributeTerm":
        return self._nodes_of_type("AttributeTerm").filter(lambda x: x.parent_id is None)[0]

    def relation_terms_of_relation_all(self, relation: "Relation") -> List["RelationTerm"]:
        return self._as_node_list(self._relation_terms_by_relation.get(relation.id_, []))

    def relation_terms_from_entity(self, entity: "Entity") -> List["RelationTerm"]:
        return self._as_node_list(self._relation_terms_by_from_entity.get(entity.id_, []))

    def relation_terms_to_entity(self, entity: "Entity") -> List["RelationTerm"]:
        return self._as_node_list(self._relation_terms_by_to_entity.get(entity.id_, []))

    def entity_terms_of_entity_all(self, entity: "Entity") -> List["EntityTerm"]:
        return self._as_node_list(self._entity_terms_by_entity.get(entity.id_, []))

    def er_terms_of_relation_term_all(self, relation_term: "RelationTerm") -> List["ERTerm"]:
        return self._as_node_list(self._er_terms_by_relation_term.get(relation_term.id_, []))

    def relation_terms_of_relation_root(self, relation: "Relation") -> List["RelationTerm"]:
        root_id = self.relation_term_root.id_
        return self.relation_terms_of_relation_all(relation).filter(lambda x: x.parent_id == root_id)

    def entity_terms_of_entity_root(self, entity: "Entity") -> List["EntityTerm"]:
        root_id = self.entity_term_root.id_
        return self.entity_terms_of_entity_all(entity).filter(lambda x: x.parent_id == root_id)

    def er_terms_of_relation_term_root(self, relation_term: "RelationTerm") -> List["ERTerm"]:
        root_id = self.er_term_root.id_
        return self.er_terms_of_relation_term_all(relation_term).filter(lambda x: x.parent_id == root_id)

    def attributes_of_node_all(self, entity: Union["Entity", "Relation"]):
        return self._as_node_list(self._attributes_by_modify.get(entity.id_, []))

    def attributes_of_node_root(self, entity: Union["Entity", "Relation"]):
        root_id = self.attribute_root.id_
        return self.attributes_of_node_all(entity).filter(lambda x: x.parent_id == root_id or (x.parent is not None and x.parent.parent_id == root_id))

    def attribute_term_of_node_all(self, item: Union["Entity", "Relation", "Attribute"]):
        nodes = []
        seen = set()
        for node in self._attribute_terms_by_modify.get(item.id_, []):
            nodes.append(node)
            seen.add(node.id_)
        for node in self._attribute_terms_by_attribute.get(item.id_, []):
            if node.id_ not in seen:
                nodes.append(node)
        return self._as_node_list(nodes)

    def attribute_term_of_node_root(self, item: Union["Entity", "Relation", "Attribute"]):
        root_id = self.attribute_term_root.id_
        return self.attribute_term_of_node_all(item).filter(lambda x: x.parent_id == root_id)

    def export(self, is_hetero=True):
        nodes, edges = [], []
        for node in self.node_dict.values():
            n, e = node.export(is_hetero)
            nodes.extend(n)
            edges.extend(e)
        return nodes, edges


if __name__ == '__main__':
    pass
    # from knowsys.tree.node import TreeNode
    # space = TreeSpace('_')
    # root = TreeNode(None, 'root', None, space)
    # root.create_child('a')
    # root.create_child('b')
    #
