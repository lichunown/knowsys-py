from typing import *

from knowsys.tree.node import TreeNode
from knowsys.enums import DirectionType

if TYPE_CHECKING:
    from knowsys.tree.space import TreeSpace


class Attribute(TreeNode):

    __inherited_properties__ = ['modify_id']

    def __init__(self, id_: Optional[str], name: str, parent: Union[str, "TreeNode", None],
                 space: Optional["TreeSpace"] = None,
                 modify_id: str = None,
                 **kwargs):
        self.modify_id = modify_id
        super().__init__(id_, name, parent, space, **kwargs)

    @property
    def modify(self):
        return self.space[self.modify_id]

    @property
    def terms_all(self):
        return self.space.attribute_term_of_node_all(self)

    @property
    def terms(self):
        return self.space.attribute_term_of_node_root(self)

    def repr_detail(self):
        return super().__repr__() + f'[t:{len(self.terms)}/{len(self.terms_all)}]'
