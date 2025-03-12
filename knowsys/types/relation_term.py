from typing import *

from knowsys.tree.node import TreeNode
from knowsys.enums import DirectionType, Direction


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
