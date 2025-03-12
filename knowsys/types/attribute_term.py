from typing import *

from knowsys.tree.node import TreeNode
from knowsys.enums import DirectionType

if TYPE_CHECKING:
    from knowsys.tree.space import TreeSpace


class AttributeTerm(TreeNode):

    __inherited_properties__ = ['attribute_id', 'modify_id']

    def __init__(self, id_: Optional[str], name: str, parent: Union[str, "TreeNode", None],
                 space: Optional["TreeSpace"] = None,
                 attribute_id: str = None, modify_id: str = None,
                 **kwargs):
        self.attribute_id = attribute_id
        self.modify_id = modify_id
        super().__init__(id_, name, parent, space, **kwargs)

    @property
    def attribute(self):
        return self.space[self.attribute_id]

    @property
    def modify(self):
        return self.space[self.modify_id]

