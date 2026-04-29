from typing import *

from knowsys.tree.node import TreeNode
from knowsys.enums import DirectionType

if TYPE_CHECKING:
    from knowsys.tree.space import TreeSpace


class EntityTerm(TreeNode):

    __inherited_properties__ = ['entity_id']

    def __init__(self, id_: Optional[str], name: str, parent: Union[str, "TreeNode", None],
                 space: Optional["TreeSpace"] = None,
                 entity_id: str = None,
                 **kwargs):

        self.entity_id = entity_id
        super().__init__(id_, name, parent, space, **kwargs)

    @property
    def entity(self):
        if self.entity_id in self.space:
            return self.space[self.entity_id]

    @property
    def attributes_terms_all(self):
        return self.entity.attributes_terms_all

    def export(self, is_hetero=True):
        nodes, edges = super().export(is_hetero)
        if self.entity_id is not None:
            edge_name = 'term_to_entity' if is_hetero else 'knowsys_edge'
            edges.append((self.id_, edge_name, self.entity_id))
            # edges.append((self.entity_id, 'has_entity_term', self.id_))
        return nodes, edges