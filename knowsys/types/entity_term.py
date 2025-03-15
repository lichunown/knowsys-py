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
        return self.space[self.entity_id]

    @property
    def attributes_terms_all(self):
        return self.entity.attributes_terms_all
