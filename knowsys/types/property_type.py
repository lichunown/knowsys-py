import typing
from typing import *
from dataclasses import dataclass

from knowsys.types.base import KnowsysType
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

    def __init__(self,
                 code: str,
                 name: str,
                 name_en: Optional[str] = None,
                 parent: Optional["PropertyType"] = None,
                 belong_to: Optional["KnowsysType"] = None):
        super().__init__(code, name, name_en, parent)

        self.belong_to = belong_to

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

