from typing import *
from knowsys.tree.node import TreeNode

if TYPE_CHECKING:
    from knowsys.tree.node import TreeNode
    from knowsys.tree.space import TreeSpace

    SpaceType = Union[TreeSpace ]
    NodeType = Union[TreeNode ]



class Entity(TreeNode):
    pass


class Relation(TreeNode):
    __inherited_properties__ = ['from_entity', 'to_entity', 'direction_type']

