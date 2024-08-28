from typing import *
from dataclasses import dataclass

from knowsys.enums import Direction
from knowsys.types.base import KnowsysType
from knowsys.collection import _KnowsysCollection
from knowsys.types.property_type import PropertyType

if TYPE_CHECKING:
    from knowsys.types.entity_type import EntityType


class RelationType(KnowsysType):
    code: str
    name: str
    name_en: Optional[str]

    parent: Optional["RelationType"]

    contain_entities: Tuple["EntityType", "EntityType"]
    direction: Direction

    def __init__(self, code: str,
                 name: str,
                 name_en: Optional[str] = None,
                 parent: Optional["KnowsysType"] = None,
                 contain_entities: Tuple["EntityType", "EntityType"] = (None, None),
                 direction: Direction = Direction.UNKNOWN):
        super().__init__(code, name, name_en, parent)
        self.contain_entities = contain_entities
        self.direction = direction

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
