import logging
import os

import numpy as np
import pandas as pd

from typing import *
from knowsys.types import *
from knowsys.enums import DirectionType, Direction
from knowsys.tree import TreeSpace
from knowsys.types import *


base_data_dir = os.path.join(os.path.split(__file__)[0], 'cached_data/')

# ##################### init ############################

# root = KnowsysType(code='1011000000000006', name='知识体系', name_en='root')
space = TreeSpace('Knowsys')
entity_type_root = Entity('105100000000000a', '实体', None, space)
relation_type_root = Relation('109500000000000b', '关系', None, space,
                              '105100000000000a', '105100000000000a')

# ##################### load entity_type / relation_type ############################
data = pd.read_csv(os.path.join(base_data_dir, 'knowsys_table_ks_system_category.csv'),
                   converters={'category_code': str, 'parent_category_code': str})
data = data[data["del_stat"] == 0]

for item in list(data.iloc)[3:]:
    if item.category_full_name_cn.startswith('实体'):
        Entity(item.category_code, item.category_name_cn, item.parent_category_code, space)

    elif item.category_full_name_cn.startswith('关系'):
        relation_con_entities: List[str] = item.category_full_name_cn.split('/')[1].split('-')
        relation_name = '/'.join(item.category_full_name_cn.split('/')[1:])
        Relation(item.category_code, relation_name, item.parent_category_code, space,
                 space.get_by_name(relation_con_entities[0]).id_, space.get_by_name(relation_con_entities[0]).id_)


# ##################### category_code Map (历史遗留原因) ############################

category_map = {
    '105101000000000b': '105101000000000b',
    '105102000000000c': '105102000000000c',
    '1051030000000000': '1051030000000000',
    '1051040000000001': '1051040000000001',
    '1051050000000002': '1051050000000002',
}
def get_category_code(code):
    return category_map.get(code, code)

# ##################### load relation type with direction ############################
data = pd.read_csv(os.path.join(base_data_dir, 'knowsys_table_ks_system_direction.csv'),
                     converters={'category_code': str, 'direction_code': str})
data = data[data["del_stat"] == 0]

direction_num_str_mapping = {
    (0, 1): "正向",
    (1, 1): "反向",
    (0, 0): "双向",
}
relation_root_root = RelationTerm(None, '关系术语', None, space,
                                   space.relation_root.id_, Direction.BiDirection)

for item in data.iloc:
    parent = space[get_category_code(item.category_code)]
    if item.directed:
        parent.direction_type = DirectionType.Direction
        if item.reversed:
            direction = Direction.Backward
        else:
            direction = Direction.Forward
    else:
        parent.direction_type = DirectionType.BiDirection
        direction = Direction.BiDirection

    RelationTerm(item.direction_code, item.reverse_expression,relation_root_root, space,
                 get_category_code(item.category_code), direction)

# ##################### load entity_term ############################

data = pd.read_csv(os.path.join(base_data_dir, 'knowsys_table_ks_system_entity.csv'),
                   converters={'category_code': str, 'entity_code': str, 'parent_entity_code': str})
data = data[(data['version_name'] == 'standard')]
data = data[data["del_stat"] == 0]

entity_term_root = EntityTerm('0000000000', '实体术语', None, space,
                              space.entity_root.id_)
for item in data.iloc:
    if item.parent_entity_code == '/':
        continue
    EntityTerm(item.entity_code, item.entity_name, item.parent_entity_code, space,
               get_category_code(item.category_code))

# ##################### load ER term ############################

data = pd.read_csv(os.path.join(base_data_dir, 'knowsys_table_ks_system_category_statement.csv'),
                   converters={'category_code': str})
data = data[data["del_stat"] == 0]
er_term_root = ERTerm(None, "实体关系术语", None, space,
                      space.entity_term_root.id_, space.relation_term_root.id_)
for item in data.iloc:
    if item.parent_statement_code == item.direction_code:
        parent = er_term_root
    else:
        parent = item.parent_statement_code
    ERTerm(item.statement_code, item.statement_content,parent, space,
           None, item.direction_code)


# ##################### load properties ############################

data = pd.read_csv(os.path.join(base_data_dir, 'knowsys_table_ks_system_property.csv'),
                   converters={'category_code': str, 'entity_code': str, 'parent_entity_code': str})
data = data[data["del_stat"] == 0]

attr_root = Attribute(None, '属性', None, space)
e_attr = Attribute(None, '实体属性', attr_root, space)
r_attr = Attribute(None, '关系属性', attr_root, space)

for item in data.iloc:
    # if item.property_code =='10a5150700600007':
    #     break
    try:
        modify = space[get_category_code(item.category_code)]
    except Exception:
        logging.warning(f'cannot found the modify {get_category_code(item.category_code)} of property {item.property_code}({item.property_name_cn})')
        continue

    Attribute(item.property_code, item.property_name_cn, e_attr, None,
              modify_id=modify.id_)

# ##################### load property terms ############################

data = pd.read_csv(os.path.join(base_data_dir, 'knowsys_table_ks_system_property_expression.csv'),
                   converters={'category_code': str, 'property_code': str,
                                 'parent_expression_code': str, 'expression_code': str})
data = data[data["del_stat"] == 0]

attr_term_root = AttributeTerm(None, '属性术语', None, space,
                               attr_root.id_)
for item in data.iloc:
    try:
        modify = space[get_category_code(item.category_code)]
    except Exception:
        logging.warning(f'cannot found the modify {get_category_code(item.category_code)} of term {item.expression_code}({item.expression_content})')
        continue
    try:
        attribute = space[item.property_code]
    except Exception:
        logging.warning(f'cannot found the attribute {item.property_code} of term {item.expression_code}({item.expression_content})')
        continue
    if item.expression_level == 0:
        parent = attr_term_root
    else:
        parent = space[item.parent_expression_code]
        if not isinstance(parent, AttributeTerm):
            logging.warning(f'The parent of AttributeTerm {item.expression_content} is logged as {parent} but it is not a AttributeTerm')
            parent = attr_term_root

    AttributeTerm(item.expression_code, item.expression_content, parent, space,
                  attribute.id_, modify.id_)

space.lazy_check()
space.fixing()
