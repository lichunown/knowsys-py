from typing import *
from knowsys.tree.node import TreeNode

if TYPE_CHECKING:
    from knowsys.tree.node import TreeNode
    from knowsys.tree.space import TreeSpace
    from knowsys.types import Entity, EntityTerm, RelationTerm, Relation, AttributeTerm, Attribute, ERTerm

    SpaceType = Union[TreeSpace ]
    NodeType = Union[TreeNode | Entity | EntityTerm | RelationTerm | Relation | AttributeTerm | Attribute | ERTerm]



