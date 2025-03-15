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

    @property
    def attributes_terms_all(self):
        res = []
        for attr in self.attributes_all:
            res.extend(attr.terms_all)
        return res

    def repr_detail(self):
        return super().__repr__() + f'[a:{len(self.attributes)}/{len(self.attributes_all)}|t:{len(self.terms)}/{len(self.terms_all)}]'
