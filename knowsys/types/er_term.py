from typing import *

from knowsys.tree.node import TreeNode
from knowsys.enums import DirectionType

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
