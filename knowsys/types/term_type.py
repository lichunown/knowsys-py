import typing
from typing import *
from dataclasses import dataclass

from knowsys.types.base import KnowsysType, _DirectData, _MappingData
from knowsys.collection import KnowsysCollection

if typing.TYPE_CHECKING:
    from knowsys.types.entity_type import EntityType
    from knowsys.types.relation_type import RelationType


class TermType(KnowsysType):
    code: str
    name: str
    name_en: Optional[str]

    parent: Optional["TermType"]
    belong_to: Optional["KnowsysType"]

    _mapping = [_DirectData('code'), _DirectData('name'), _DirectData('name_en'),
                _MappingData('parent'), _MappingData('belong_to')]

    def __init__(self,
                 code: str,
                 name: str,
                 name_en: Optional[str] = None,
                 parent: Optional["TermType"] = None,
                 belong_to: Optional["KnowsysType"] = None):
        super().__init__(code, name, name_en, parent)

        self.belong_to = belong_to

    def create_child(self, name, code=None, name_en=None):
        res = super().create_child(name, code, name_en)
        res.belong_to = self.belong_to
        return res


class EntityTermType(TermType):
    code: str
    name: str
    name_en: Optional[str]

    parent: Optional["TermType"]
    belong_to: Optional["EntityType"]

    def __init__(self,
                 code: str,
                 name: str,
                 name_en: Optional[str] = None,
                 parent: Optional["KnowsysType"] = None,
                 belong_to: Optional["EntityType"] = None):
        super().__init__(code, name, name_en, parent, belong_to)


class RelationTermType(TermType):
    code: str
    name: str
    name_en: Optional[str]

    parent: Optional["TermType"]
    belong_to: Optional["RelationType"]

    def __init__(self,
                 code: str,
                 name: str,
                 name_en: Optional[str] = None,
                 parent: Optional["KnowsysType"] = None,
                 belong_to: Optional["RelationType"] = None):
        super().__init__(code, name, name_en, parent, belong_to)


class PropertyTermType(TermType):
    code: str
    name: str
    name_en: Optional[str]

    parent: Optional["TermType"]
    belong_to: Optional["RelationType"]

    def __init__(self,
                 code: str,
                 name: str,
                 name_en: Optional[str] = None,
                 parent: Optional["KnowsysType"] = None,
                 belong_to: Optional["RelationType"] = None):
        super().__init__(code, name, name_en, parent, belong_to)

