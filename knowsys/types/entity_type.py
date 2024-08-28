from typing import *
from dataclasses import dataclass

from knowsys.types.base import KnowsysType
from knowsys.collection import KnowsysCollection, _KnowsysCollection


class EntityType(KnowsysType):
    code: str
    name: str
    name_en: Optional[str]

    parent: Optional["EntityType"]

    def __init__(self,
                 code: str,
                 name: str,
                 name_en: Optional[str] = None,
                 parent: Optional["KnowsysType"] = None):
        super().__init__(code, name, name_en, parent)

    def relations_start_by(self, refresh=True):
        from knowsys.types.relation_type import RelationType
        if refresh:
            setattr(self, '_relations_start_from',
                    list(filter(lambda item: isinstance(item, RelationType) and item.from_entity == self,
                                KnowsysCollection.instance.data)))
        return getattr(self, '_relations_start_from', None)

    def relations_end_by(self, refresh=True):
        from knowsys.types.relation_type import RelationType
        if refresh:
            setattr(self, '_relations_end_by',
                    list(filter(lambda item: isinstance(item, RelationType) and item.to_entity == self,
                                KnowsysCollection.instance.data)))
        return getattr(self, '_relations_end_by', None)

    def properties(self, refresh=True) -> _KnowsysCollection:
        from knowsys.types.property_type import PropertyType
        if refresh:
            setattr(self, '_properties',
                    self.collection.filter(lambda item: isinstance(item, PropertyType) and item.belong_to == self)),
        return getattr(self, '_properties', None)

    def properties_with_parents(self, refresh=True) -> _KnowsysCollection:
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
        from knowsys.types.term_type import EntityTermType
        if refresh:
            setattr(self, '_terms',
                    self.collection.filter(lambda item: isinstance(item, EntityTermType) and item.parent is None and item.belong_to == self))
        return getattr(self, '_terms', None)

    def terms_with_children(self):
        res = self.terms()
        for item in self.contains():
            res.extend(item.terms_with_children())
        return res
