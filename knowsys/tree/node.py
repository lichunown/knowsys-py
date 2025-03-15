from typing import *

from knowsys.tree.space import TreeSpace
from knowsys.tree.utils import random_string

if TYPE_CHECKING:
    from knowsys.tree._types import SpaceType, NodeType


class TreeNode(object):
    id_: str
    name: str
    parent_id: str
    space: "SpaceType"

    __inherited_properties__ = []

    def __hash__(self):
        return self.id_.__hash__()

    def __getitem__(self, item):
        return self.children[item]

    def __init__(self, id_: Optional[str], name: str, parent: Union[str, "TreeNode", None],
                 space: Optional["SpaceType"] = None, **kwargs):
        if id_ is None:
            id_ = random_string()

        self.id_ = id_
        self.name = name

        if isinstance(parent, TreeNode):
            if space is not None:
                assert parent.space == space
            space = parent.space
            parent = parent.id_
        self.parent_id = parent

        if space is None:
            raise ValueError('cannot found a space to create')

        self.space = space
        self.space[self.id_] = self

        self._lazy_check_funcs = []

        def _lazy_check_func():
            if self.parent is not None:
                assert isinstance(self.parent, self.__class__), (f'The node type ({self.__class__.__name__}) '
                                                                 f'{self.id_}:{self.name} is different with its parent '
                                                                 f'type ({self.parent.__class__.__name__}) '
                                                                 f'{self.parent.id_}:{self.parent.name}')
            for k in self.__inherited_properties__:
                if self.parent is not None:
                    if getattr(self, k, None) is None:
                        setattr(self, k, getattr(self.parent, k))
            for k, v in kwargs.items():
                # setattr(self, k, v)
                raise ValueError(f'cannot parse the input param {k}:{v}')
        if self.parent_id in self.space:
            _lazy_check_func()
        else:
            self.set_lazy_check(_lazy_check_func)

    def set_lazy_check(self, func):
        self._lazy_check_funcs.append(func)

    def lazy_check(self):
        for func in self._lazy_check_funcs:
            func()

    def create_child(self, name: str, id_: Optional[str]=None, **kwargs):
        return self.__class__(id_, name, self, self.space, **kwargs)

    @classmethod
    def from_dict(cls, data: Dict[str, Dict], self_name='default', tree_space_class=TreeSpace):
        space = tree_space_class('_')
        root = cls(random_string(), self_name, None, space)

        def _travel_from_dict(children: Dict, parent_id):
            for child_name, child_data in children.items():
                child = cls(random_string(), child_name, parent_id, space)
                _travel_from_dict(child_data, child.id_)

        _travel_from_dict(data, root.id_)
        return root

    def children_to_dict(self) -> Dict[str, Dict]:
        return {child.name: child.children_to_dict() for child in self.children}

    @property
    def parent(self) -> Optional["NodeType"]:
        if self.parent_id is None:
            return None
        return self.space[self.parent_id]

    @property
    def brothers(self) -> List["NodeType"]:
        from knowsys.tree.node_list import NodeList
        if self.parent is None:
            return []
        res = self.parent.children.copy()
        res.remove(self)
        return NodeList(res)

    def deepcopy(self) -> "NodeType":
        new_space = self.space.deepcopy()
        return new_space[self.id_]

    @property
    def children(self) -> List["NodeType"]:
        from knowsys.tree.node_list import NodeList
        return NodeList(self.space.get_children_of_node(self.id_))

    @property
    def is_leaf(self):
        return len(self.children) == 0

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    def repr_detail(self):
        return self.__repr__()

    def _repr_self(self, **kwargs):
        return self.repr_detail()

    def _children_for_print(self):
        return self.children

    def _tree_string(self, level=2, space=0, **kwargs):

        def _space():
            return '    ' * (space - 1) + '  |-' if space >= 1 else ''

        res = _space() + self._repr_self(**kwargs) + '\n'
        if level > 1:
            for child in self._children_for_print():
                res += child._tree_string(level - 1, space + 1)

        return res

    def print_tree(self, level=10, **kwargs):
        print(self._tree_string(level, **kwargs))

    def __eq__(self, other: "NodeType"):
        if not isinstance(other, TreeNode):
            raise ValueError(f'[{self}] compare to {other}, but it is not NodeType')
        return self.id_ == other.id_

    def child_eq(self, other: "NodeType"):
        if not isinstance(other, TreeNode):
            raise ValueError
        if tuple(sorted([item.name for item in self.children])) != tuple(sorted([item.name for item in other.children])):
            return False
        for child in self.children:
            if not any([child == c for c in list(filter(lambda x: x.name == child.name, other.children))]):
                return False
        return True

    @property
    def depth(self) -> int:
        child_depth_list = [child.depth for child in self.children]
        child_depth = max(child_depth_list) if len(child_depth_list) > 0 else 0
        return child_depth + 1

    @property
    def level(self) -> int:
        if self.parent is None:
            return 0
        return self.parent.level + 1



if __name__ == '__main__':
    root = TreeNode(None, 'root', None)

