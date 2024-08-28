from typing import *
from dataclasses import dataclass

from knowsys.enums import Direction
from knowsys.types.base import KnowsysType, _DirectData, _MappingData, _DirectionData
from knowsys.collection import _KnowsysCollection, _LazyLoadType
from knowsys.types.property_type import PropertyType

if TYPE_CHECKING:
    from knowsys.types.entity_type import EntityType


class _TupleData(str):
    pass


class RelationType(KnowsysType):
    code: str
    name: str
    name_en: Optional[str]

    parent: Optional["RelationType"]

    contain_entities: Tuple["EntityType", "EntityType"]
    direction: Direction

    _mapping = [_DirectData('code'), _DirectData('name'), _DirectData('name_en'),
                _MappingData('parent'), _TupleData('contain_entities'), _DirectionData('direction')]

    def saving_list(self) -> List[str]:
        res = []
        for item in self._mapping:
            if isinstance(item, _DirectData):
                res.append(getattr(self, item))
            elif isinstance(item, _MappingData):
                item = getattr(self, item)
                if item is None:
                    res.append('')
                else:
                    res.append(item.code)
            elif isinstance(item, _DirectionData):
                res.append(getattr(self, item).name)
            elif isinstance(item, _TupleData):
                res.append('|'.join([i.code for i in getattr(self, item)]))
            else:
                raise TypeError(f'Unexpected type {type(item)}')
        return res

    @classmethod
    def load_list(cls, data: List[str]):
        inputs = {}
        for key, value in zip(cls._mapping, data):
            if isinstance(key, _DirectData):
                inputs[key] = value
            elif isinstance(key, _MappingData):
                inputs[key] = _LazyLoadType(value, None)
            elif isinstance(key, _DirectionData):
                inputs[key] = getattr(Direction, value)
            elif isinstance(key, _TupleData):
                inputs[key] = tuple([_LazyLoadType(item, None) for item in value.split('|')])
            else:
                raise TypeError(f'Unexpected type {type(key)}')
        return cls(**inputs)

    def __init__(self, code: str,
                 name: str,
                 name_en: Optional[str] = None,
                 parent: Optional["KnowsysType"] = None,
                 contain_entities: Tuple["EntityType", "EntityType"] = (None, None),
                 direction: Direction = Direction.UNKNOWN):
        super().__init__(code, name, name_en, parent)
        self.contain_entities = contain_entities
        self.direction = direction

    def create_child(self, name, code=None, name_en=None,
                     contain_entities: Tuple["EntityType", "EntityType"] = None,
                     direction: Direction = None):
        if contain_entities is None:
            contain_entities = self.contain_entities
        if direction is None:
            direction = self.direction

        res = super().create_child(name, code, name_en)
        res.contain_entities = contain_entities
        res.direction = direction
        return res

    @property
    def from_entity(self):
        if self.direction in [Direction.FORWARD, Direction.BI_DIRECTION]:
            return self.contain_entities[0]
        elif self.direction == Direction.BACKWARD:
            return self.contain_entities[-1]
        return None

    @property
    def to_entity(self):
        if self.direction in [Direction.FORWARD, Direction.BI_DIRECTION]:
            return self.contain_entities[-1]
        elif self.direction == Direction.BACKWARD:
            return self.contain_entities[0]
        return None

    def properties(self, refresh=True):
        if refresh:
            setattr(self, '_properties',
                    self.collection.filter(lambda item: isinstance(item, PropertyType) and item.belong_to == self))
        return getattr(self, '_properties', None)

    def properties_with_parents(self, refresh=True) -> "_KnowsysCollection":
        if refresh:
            p = self.properties()
            tmp = self.parent
            while tmp is not None:
                for pp in tmp.properties():
                    if not p.contain_with_parent(pp):
                        p._add(pp)
                tmp = tmp.parent
            setattr(self, '_property_with_parents', p)
        return getattr(self, '_property_with_parents', None)

    def terms(self, refresh=True):
        from knowsys.types.term_type import RelationTermType
        if refresh:
            setattr(self, '_terms',
                    self.collection.filter(lambda item: isinstance(item, RelationTermType) and item.parent is None and item.belong_to == self))
        return getattr(self, '_terms', None)

    def terms_with_children(self):
        res = self.terms()
        for item in self.contains():
            res.extend(item.terms_with_children())
        return res
