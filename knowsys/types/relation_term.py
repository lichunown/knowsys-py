from typing import *

from knowsys.tree.node import TreeNode
from knowsys.enums import Direction


if TYPE_CHECKING:
    from knowsys.tree.space import TreeSpace
    from knowsys.types import Relation


class RelationTerm(TreeNode):

    __inherited_properties__ = ['relation_id', 'direction']

    def __init__(self, id_: Optional[str], name: str, parent: Union[str, "TreeNode", None],
                 space: Optional["TreeSpace"] = None,
                 relation_id: str = None,
                 direction: Direction = None,
                 **kwargs):

        self.relation_id = relation_id
        self.direction = direction
        super().__init__(id_, name, parent, space, **kwargs)

    @property
    def relation(self) -> "Relation":
        return self.space[self.relation_id]

    @property
    def from_entity(self):
        if self.direction < 0:
            return self.relation.to_entity
        return self.relation.from_entity

    @property
    def to_entity(self):
        if self.direction < 0:
            return self.relation.from_entity
        return self.relation.to_entity

    @property
    def er_terms(self):
        return self.space.er_terms_of_relation_term_root(self)

    @property
    def er_terms_all(self):
        return self.space.er_terms_of_relation_term_all(self)

    def _children_for_print(self):
        if len(self.children) == 0:
            return self.er_terms
        return self.children

    def repr_detail(self):
        return super().__repr__() + f'{{{"|".join([item.name for item in self.attributes_terms_all])}}}'

    @property
    def attributes_terms_all(self):
        res = []
        for attr in self.relation.attributes_all:
            res.extend(attr.terms_all)
        return res

    def export(self, is_hetero=True):
        nodes, edges = super().export(is_hetero)
        if self.relation_id is not None:
            edge_name = 'belong_to_relation' if is_hetero else 'knowsys_edge'
            edges.append((self.id_, edge_name, self.relation_id))
            # edges.append((self.relation_id, 'has_relation_term', self.id_))
        return nodes, edges
