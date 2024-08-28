import logging
import typing

import numpy as np
from collections import defaultdict, Counter
from typing import *

if typing.TYPE_CHECKING:
    from knowsys.types.base import KnowsysAllType


class _KnowsysCollection(object):

    def __init__(self,
                 data: List["KnowsysAllType"] = None,
                 code2item: Dict[str, "KnowsysAllType"] = None,
                 name2item: Dict[str, List["KnowsysAllType"]] = None):

        self._data: List["KnowsysAllType"] = []
        if data is not None:
            self._data = data

        self._code2item: Dict[str, "KnowsysAllType"] = {}
        if code2item is not None:
            assert len(code2item) == len(self._data), \
                f'len(code2item):{len(code2item)} is not equal to len(data): {len(self._data)}'
            self._code2item = code2item
        else:
            for item in self._data:
                self._code2item[item.code] = item

        self._name2item: Dict[str, List["KnowsysAllType"]] = defaultdict(list)
        if name2item is not None:
            assert sum([len(v) for v in name2item.values()]) == len(self._data), \
                (f'len(name2item):{sum([len(v) for v in name2item.values()])} '
                 f'is not equal to len(data): {len(self._data)}')
            self._name2item = name2item
        else:
            for item in self._data:
                self._name2item[item.name].append(item)

    def contain_with_parent(self, item):
        from knowsys.types.base import KnowsysAllType
        if not isinstance(item, KnowsysAllType):
            raise TypeError(f'item is not a KnowsysAllType: {item}')
        for item in self._data:
            if isinstance(item, KnowsysAllType) and item.is_belong_to(item):
                return True
        return False

    def __contains__(self, item):
        from knowsys.types.base import KnowsysAllType
        if isinstance(item, KnowsysAllType):
            code = item.code
        elif isinstance(item, str):
            code = item
        else:
            raise ValueError
        return code in self._code2item

    @property
    def data(self):
        return self._data

    def _add(self, knowsys_item: "KnowsysAllType"):
        self._data.append(knowsys_item)
        self._code2item[knowsys_item.code] = knowsys_item
        self._name2item[knowsys_item.name].append(knowsys_item)

    def find(self, code: str, default=None):
        return self._code2item.get(code, default)

    get = find

    def find_name(self, name: str, findall=True, default=None):
        if findall:
            return self._name2item.get(name, [default])
        else:
            r = self._name2item.get(name, [])
            if len(r) > 0:
                return r[0]
            else:
                return default

    def filter(self, func: Callable) -> "_KnowsysCollection":
        data = list(filter(func, self._data))
        return _KnowsysCollection(data,
                                  {item.code: self._code2item[item.code] for item in data},
                                  None)

    def map(self, func: Callable):
        from knowsys.types.base import KnowsysType
        data = list(map(func, self._data))
        if all([isinstance(item, KnowsysType) for item in data]):
            data = _KnowsysCollection(data)
        return data

    def extend(self, items):
        for item in items:
            self._add(item)

    def flatten(self):
        from knowsys.types.base import KnowsysType
        res = _KnowsysCollection()
        for item in self._data:
            if isinstance(item, KnowsysType):
                res.extend(item.flatten())
        return res

    def _filter_by_type(self, knowsys_type_class: type):
        return self.filter(lambda x: isinstance(x, knowsys_type_class))

    @property
    def entity_types(self):
        from knowsys.types import EntityType
        return self._filter_by_type(EntityType)

    @property
    def relation_types(self):
        from knowsys.types import RelationType
        return self._filter_by_type(RelationType)

    @property
    def term_types(self):
        from knowsys.types.term_type import TermType
        return self._filter_by_type(TermType)

    @property
    def entity_term_types(self):
        from knowsys.types.term_type import EntityTermType
        return self._filter_by_type(EntityTermType)

    @property
    def relation_term_types(self):
        from knowsys.types.term_type import RelationTermType
        return self._filter_by_type(RelationTermType)

    # TODO: add types

    def list(self):
        return list(self)

    def __getitem__(self, item):
        return self._data.__getitem__(item)

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
        return self._data.__len__()

    def count_summary(self):
        return dict(Counter([item.__class__.__name__ for item in self.data]))

    def __repr__(self):
        return f'_KnowsysCollection(total:{len(self._data)}|{self.count_summary()})'


class _LazyLoadType(object):

    def __init__(self, code, name):
        self.code = code
        self.name = name

    def real(self):
        if self.code is not None:
            return KnowsysCollection.instance.get(self.code)
        elif self.name is not None:
            return KnowsysCollection.instance.find_name(self.name, findall=False)


class KnowsysCollection(_KnowsysCollection):

    instance: "KnowsysCollection" = None

    def __init__(self):
        if self.instance is not None:
            raise EnvironmentError('the collection only can be init ones.')

        super().__init__()
        self.__class__.instance = self

    def add(self, knowsys_item: "KnowsysAllType", skip=False):
        if knowsys_item.code in self._code2item:
            if skip:
                return
            raise ValueError(f'`{knowsys_item}` has been created in KnowsysCollection.')
        self._add(knowsys_item)

    def lazy_get(self, code: str = None, name: str = None):
        if code is not None:
            res = self.get(code)
        elif name is not None:
            res = self.find_name(name, findall=False)
        else:
            raise ValueError

        if res is None:
            return _LazyLoadType(code, name)
        return res

    def check_lazy(self):
        for item in self._data:
            for k, v in item.__dict__.items():
                if isinstance(v, _LazyLoadType):
                    real_v = v.real()
                    if real_v is None:
                        logging.warning(f'Cannot found knowsys item: `{v.code}`.')
                    setattr(item, k, real_v)


knowsys_collection = KnowsysCollection()
