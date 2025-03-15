from typing import *

from knowsys.tree.node import TreeNode
from knowsys.enums import DirectionType

if TYPE_CHECKING:
    from knowsys.tree.space import TreeSpace


class Relation(TreeNode):

    __inherited_properties__ = ['from_entity_id', 'to_entity_id', 'direction_type']

    def __init__(self, id_: Optional[str], name: str, parent: Union[str, "TreeNode", None],
                 space: Optional["TreeSpace"] = None,
                 from_entity_id: str = None, to_entity_id: str = None, direction_type: DirectionType = DirectionType.UNKNOWN,
                 **kwargs):

        self.from_entity_id = from_entity_id
        self.to_entity_id = to_entity_id
        self.direction_type = direction_type

        super().__init__(id_, name, parent, space, **kwargs)

    @property
    def from_entity(self):
        return self.space[self.from_entity_id]

    @property
    def to_entity(self):
        return self.space[self.to_entity_id]

    @property
    def terms_all(self):
        return self.space.relation_terms_of_relation_all(self)

    @property
    def terms(self):
        return self.space.relation_terms_of_relation_root(self)

    @property
    def attributes(self):
        return self.space.attributes_of_node_root(self)

    @property
    def attributes_all(self):
        return self.space.attributes_of_node_all(self)

    def repr_detail(self):
        return super().__repr__() + f'[a:{len(self.attributes)}/{len(self.attributes_all)}|t:{len(self.terms)}/{len(self.terms_all)}]'

    def _children_for_print(self):
        if len(self.children) == 0:
            return self.terms
        return self.children
