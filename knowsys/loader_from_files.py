import logging
import os

import numpy as np
import pandas as pd

from typing import *
from knowsys.types import *
from knowsys.enums import Direction
from knowsys.collection import knowsys_collection


base_data_dir = os.path.join(os.path.split(__file__)[0], 'cached_data/')

# ##################### init ############################

root = KnowsysType(code='1011000000000006', name='知识体系', name_en='root')
entity_type_root = EntityType('105100000000000a', '实体', 'entity', root)
relation_type_root = RelationType('109500000000000b', '关系', 'relation', root,
                                  contain_entities=(entity_type_root, entity_type_root))

setattr(knowsys_collection, 'root', root)
setattr(knowsys_collection, 'relation_root', relation_type_root)
setattr(knowsys_collection, 'entity_root', entity_type_root)

# ##################### load entity_type / relation_type ############################

data = pd.read_excel(os.path.join(base_data_dir, 'ks_system_category.xlsx'),
                     converters={'category_code': str, 'parent_category_code': str})

for item in list(data.iloc)[3:]:
    if item.category_full_name_cn.startswith('实体'):
        EntityType(item.category_code,
                   item.category_name_cn,
                   item.category_name,
                   knowsys_collection.lazy_get(item.parent_category_code))
    elif item.category_full_name_cn.startswith('关系'):
        relation_con_entities: List[str] = item.category_full_name_cn.split('/')[1].split('-')
        relation_name = '/'.join(item.category_full_name_cn.split('/')[1:])
        RelationType(item.category_code,
                     relation_name,  # item.category_name_cn
                     item.category_name,
                     knowsys_collection.lazy_get(item.parent_category_code),
                     contain_entities=(knowsys_collection.lazy_get(name=relation_con_entities[0]),
                                       knowsys_collection.lazy_get(name=relation_con_entities[1])),
                     direction=Direction.UNKNOWN)
knowsys_collection.check_lazy()

# ##################### load relation type with direction ############################

data = pd.read_excel(os.path.join(base_data_dir, 'ks_system_direction.xlsx'),
                     converters={'category_code': str, 'direction_code': str})

direction_num_str_mapping = {
    (0, 1): "正向",
    (1, 1): "反向",
    (0, 0): "双向",
}

for item in data.iloc:
    parent = knowsys_collection.get(item.category_code)
    RelationType(item.direction_code,
                 item.reverse_expression,
                 '', parent,
                 (knowsys_collection.get(item.origin),
                  knowsys_collection.get(item.destination)),
                 Direction.from_str(direction_num_str_mapping[(item.reversed, item.directed)]))

# ##################### load entity_term ############################

data = pd.read_excel(os.path.join(base_data_dir, 'ks_system_entity.xlsx'),
                     converters={'category_code': str, 'entity_code': str, 'parent_entity_code': str})
data = data[(data['version_name'] == 'Standard')]
l1_data = data[data['parent_entity_code'] == '0000000000']
for item in l1_data.iloc:
    EntityTermType(item.entity_code,
                   item.entity_name,
                   '', None,
                   knowsys_collection.lazy_get(item.category_code))

other_data = data[(data['parent_entity_code'] != '0000000000') & (data['parent_entity_code'] != '/')]
for item in other_data.iloc:
    EntityTermType(item.entity_code,
                   item.entity_name,
                   '',
                   knowsys_collection.lazy_get(item.parent_entity_code),
                   knowsys_collection.lazy_get(item.category_code))
knowsys_collection.check_lazy()

# ##################### load relation term ############################

data = pd.read_excel(os.path.join(base_data_dir, 'ks_system_category_statement.xlsx'),
                     converters={'category_code': str})
data = data[data["del_stat"] == 0]
for item in data.iloc:
    RelationTermType(item.statement_code, item.statement_content,
                     '', None,
                     knowsys_collection.lazy_get(item.parent_statement_code))

knowsys_collection.check_lazy()

# ##################### load properties ############################

data = pd.read_excel(os.path.join(base_data_dir, 'ks_system_property.xlsx'),
                     converters={'category_code': str, 'entity_code': str, 'parent_entity_code': str})
for item in data.iloc:
    belong_to = knowsys_collection.get(item.category_code)
    if isinstance(belong_to, EntityType):
        EntityPropertyType(item.property_code, item.property_name_cn,
                           item.property_name, None,
                           belong_to=belong_to)
    elif isinstance(belong_to, RelationType):
        RelationPropertyType(item.property_code, item.property_name_cn,
                             item.property_name, None,
                             belong_to=belong_to)

# ##################### load property terms ############################

data = pd.read_excel(os.path.join(base_data_dir, 'ks_system_property_expression.xlsx'),
                     converters={'category_code': str, 'property_code': str,
                                 'parent_expression_code': str, 'expression_code': str})
for item in data.iloc:
    belong_to = knowsys_collection.get(item.property_code)
    if item.expression_level == 1:
        parent = None
    else:
        parent = knowsys_collection.lazy_get(item.parent_expression_code)
    if isinstance(belong_to, EntityType):
        EntityPropertyType(item.expression_code, item.expression_content,
                           '', parent, belong_to)
    elif isinstance(belong_to, RelationType):
        RelationPropertyType(item.expression_code, item.expression_content,
                             '', parent, belong_to)


