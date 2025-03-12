from typing import *

from knowsys.tree.node import TreeNode

if TYPE_CHECKING:
    from knowsys.tree.space import TreeSpace


class Entity(TreeNode):
    def __init__(self, id_: Optional[str], name: str, parent: Union[str, "TreeNode", None],
                 space: Optional["TreeSpace"] = None, **kwargs):
        super().__init__(id_, name, parent, space, **kwargs)

    @property
    def terms_all(self):
        return self.space.entity_terms_of_entity_all(self)

    @property
    def terms(self):
        return self.space.entity_terms_of_entity_root(self)

    @property
    def attributes(self):
        return self.space.attributes_of_node_root(self)

    @property
    def attributes_all(self):
        return self.space.attributes_of_node_all(self)
