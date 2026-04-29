from typing import *

from knowsys.tree.node import TreeNode
from knowsys.types import RelationTerm, EntityTerm

if TYPE_CHECKING:
    from knowsys.tree.space import TreeSpace


class ERTerm(TreeNode):

    __inherited_properties__ = ['entity_term_id', 'relation_term_id']

    def __init__(self, id_: Optional[str], name: str, parent: Union[str, "TreeNode", None],
                 space: Optional["TreeSpace"] = None,
                 entity_term_id: str = None,
                 relation_term_id: str = None,
                 **kwargs):
        self.entity_term_id = entity_term_id
        self.relation_term_id = relation_term_id
        super().__init__(id_, name, parent, space, **kwargs)

    @property
    def entity_term(self) -> "EntityTerm":
        return self.space[self.entity_term_id]

    @property
    def relation_term(self) -> "RelationTerm":
        return self.space[self.relation_term_id]

    @property
    def attributes_terms_all(self):
        return self.relation_term.attributes_terms_all

    def repr_detail(self):
        return super().__repr__()

    def export(self, is_hetero=True):
        nodes, edges = super().export(is_hetero)
        if self.entity_term_id is not None:
            edge_name = 'conn_entity_term' if is_hetero else 'knowsys_edge'
            edges.append((self.id_, edge_name, self.entity_term_id))
            # edges.append((self.entity_term_id, 'e_has_er_term', self.id_))
        if self.relation_term_id is not None:
            edge_name = 'conn_relation_term' if is_hetero else 'knowsys_edge'
            edges.append((self.id_, edge_name, self.relation_term_id))
            # edges.append((self.relation_term_id, 'r_has_er_term', self.id_))
        return nodes, edges
