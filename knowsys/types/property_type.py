import typing
from typing import *
from dataclasses import dataclass

from knowsys.types.base import KnowsysType, _DirectData, _MappingData
from knowsys.collection import KnowsysCollection

if typing.TYPE_CHECKING:
    from knowsys.types.entity_type import EntityType
    from knowsys.types.relation_type import RelationType


class PropertyType(KnowsysType):
    code: str
    name: str
    name_en: Optional[str]

    parent: Optional["PropertyType"]
    belong_to: Optional["KnowsysType"]

    _mapping = [_DirectData('code'), _DirectData('name'), _DirectData('name_en'),
                _MappingData('parent'), _MappingData('belong_to')]

    def __init__(self,
                 code: str,
                 name: str,
                 name_en: Optional[str] = None,
                 parent: Optional["PropertyType"] = None,
                 belong_to: Optional["KnowsysType"] = None):
        super().__init__(code, name, name_en, parent)

        self.belong_to = belong_to

    def create_child(self, name, code=None, name_en=None):
        res = super().create_child(name, code, name_en)
        res.belong_to = self.belong_to
        return res

    def terms(self, refresh=True):
        from knowsys.types.term_type import PropertyTermType
        if refresh:
            setattr(self, '_terms',
                    self.collection.filter(lambda item: isinstance(item, PropertyTermType) and item.parent is None and item.belong_to == self))
        return getattr(self, '_terms', None)

    def terms_with_children(self):
        res = self.terms()
        for item in self.contains():
            res.extend(item.terms_with_children())
        return res


class EntityPropertyType(PropertyType):
    code: str
    name: str
    name_en: Optional[str]

    parent: Optional["PropertyType"]
    belong_to: Optional["EntityType"]


class RelationPropertyType(PropertyType):
    code: str
    name: str
    name_en: Optional[str]

    parent: Optional["PropertyType"]
    belong_to: Optional["RelationType"]

