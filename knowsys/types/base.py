import logging

from dataclasses import dataclass
from knowsys.collection import knowsys_collection, _KnowsysCollection
from typing import *


class KnowsysType(object):
    collection = knowsys_collection

    def __init__(self,
                 code: str,
                 name: str,
                 name_en: Optional[str] = None,
                 parent: Optional["KnowsysType"] = None):

        self.code: str = code
        self.name: str = name
        self.name_en: Optional[str] = name_en
        self.parent: Optional["KnowsysType"] = parent

        if self.code in self.collection:
            logging.error(f'Redefined error. <code: {code}|name: {name}>,'
                          f' exists: {self.collection.get(code)}')
        else:
            self.collection.add(self)

    @property
    def Code(self):
        from knowsys.code import Code
        return Code.of(self.code)

    def is_belong_to(self, other):
        tmp = self.parent
        while tmp is not None:
            if tmp == other:
                return True
            tmp = tmp.parent
        return False

    def contains(self, refresh=True):
        if refresh:
            setattr(self, '_contains',
                    self.collection.filter(lambda item: item.parent == self))
        return getattr(self, '_contains', None)

    def flatten(self) -> _KnowsysCollection:
        res = [self]
        for child in self.contains():
            res.extend(child.flatten())
        return _KnowsysCollection(res)

    def __getitem__(self, item):
        return self.contains()[item]

    def __copy__(self):
        return self

    def __deepcopy__(self):
        return self

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        if not isinstance(other, KnowsysType):
            return False
        return other.code == self.code

    def __repr__(self):
        return f'{self.__class__.__name__}({self.code}:{self.name})'

    def __str__(self):
        return self.name

    def properties(self):
        return _KnowsysCollection()

    def terms(self):
        return _KnowsysCollection()


KnowsysAllType = Union[KnowsysType]

if __name__ == '__main__':
    a = KnowsysType('aaa', 'aaa')
    b = KnowsysType('bbb', 'bbb', parent=knowsys_collection.lazy_get('aaa'))
    c = KnowsysType('ccc', 'ccc', parent=knowsys_collection.lazy_get('aaa'))

    e = KnowsysType('eee', 'eee', parent=knowsys_collection.lazy_get('ddd'))
    f = KnowsysType('fff', 'fff', parent=knowsys_collection.lazy_get(name='ddd'))
    d = KnowsysType('ddd', 'ddd')

    knowsys_collection.check_lazy()
    knowsys_collection.get('aaa').contains()
