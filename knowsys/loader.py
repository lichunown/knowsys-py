import logging
import os

import numpy as np
import pandas as pd

from typing import *
from knowsys.types import *
from knowsys.enums import Direction
from utils.sql_loader import auto_load_table_from_sql

from global_config import KNOWSYS_LOAD_FROM_SQL as LOAD_FROM_SQL


base_data_dir = os.path.join(os.path.split(__file__)[0], 'cached_data/')


# ##################### load entity ############################
root = KnowsysItem('root', code='1011000000000006')
term_collection.append(root)

data = auto_load_table_from_sql(base_data_dir, 'knowsys_', 'ks_system_category',
                                LOAD_FROM_SQL, 'knowsys_',
                                converters={'category_code': str, 'parent_category_code': str})

entity_root = EntityType('实体', '105100000000000a')
entity_root.parent = root
term_collection.append(entity_root)

relation_root = Relation('关系',
                         term_collection.find_term_by_code('105100000000000a'),  # noqa
                         term_collection.find_term_by_code('105100000000000a'),  # noqa
                         code='109500000000000b')
relation_root.parent = root
term_collection.append(relation_root)


def load_entity(code):
    item = data[data['category_code'] == code].iloc[0]
    if term_collection.find_term_by_code(code):
        return term_collection.find_term_by_code(code)
    if item.category_full_name_cn.startswith('实体'):
        parent = term_collection.find_term_by_code(item.parent_category_code)
        if parent is None:
            parent = load_entity(item.parent_category_code)
        res = EntityType(item.category_name_cn, item.category_code, parent)
        term_collection.append(res)
        return res


for item in list(data.iloc)[2:]:
    load_entity(item.category_code)


# ##################### load relation ############################


def load_relation(code):
    item = data[data['category_code'] == code].iloc[0]
    if term_collection.find_term_by_code(code):
        return term_collection.find_term_by_code(code)

    if item.category_full_name_cn.startswith('关系'):
        parent = term_collection.find_term_by_code(item.parent_category_code)
        if parent is None:
            load_relation(item.parent_category_code)
            parent = term_collection.find_term_by_code(item.parent_category_code)

        from_to = item.category_full_name_cn.split('/')
        if len(from_to) > 1:
            from_term_str, to_item_str = from_to[1].split('-')
        else:
            from_term_str, to_item_str = None, None

        res = Relation(item.category_name_cn,
                       term_collection.find_terms_by_name(from_term_str)[0],  # noqa
                       term_collection.find_terms_by_name(to_item_str)[0],    # noqa
                       Direction.UNKNOWN,
                       item.category_code,
                       parent)  # noqa
        term_collection.append(res)


for item in list(data.iloc)[3:]:
    load_relation(item.category_code)


# ##################### load direction ############################


data = auto_load_table_from_sql(base_data_dir, 'knowsys_', 'ks_system_direction',
                                LOAD_FROM_SQL, 'knowsys_',
                                converters={'category_code': str, 'direction_code': str})
# data = data[data["del_stat"] == 0]

direction_num_str_mapping = {
    (0, 1): "正向",
    (1, 1): "反向",
    (0, 0): "双向",
}

direction_map = {}
for item in data.iloc:
    if term_collection.find_term_by_code(item.category_code) is None:
        print(f'cannot found code: {item.category_code}')
        continue
    parent = term_collection.find_term_by_code(item.category_code)
    child = parent.create_relation(parent.name + '_' + direction_num_str_mapping[(item.reversed, item.directed)],
                                   Direction.from_str(direction_num_str_mapping[(item.reversed, item.directed)]),
                                   parent.from_entity, parent.to_entity,
                                   code=item.direction_code)
    term_collection.append(child)


# ##################### load relation term ############################


data = auto_load_table_from_sql(base_data_dir, 'knowsys_', 'ks_system_category_statement',
                                LOAD_FROM_SQL, 'knowsys_',
                                converters={'category_code': str})
data = data[data["del_stat"] == 0]

# for level in range(1, max(data['statement_level']) + 1):
l1_data = data[data["statement_level"] == 1]


for item in l1_data.iloc:
    parent = term_collection.find_term_by_code(item.direction_code)
    if parent is None:
        continue
    child = parent.create_term(item.statement_content, code=item.statement_code)
    term_collection.append(child)

for level in range(2, max(data["statement_level"]) + 1):
    tmp_data = data[data["statement_level"] == level]
    for item in tmp_data.iloc:
        # direction_str_term = direction_map.get(item.direction_code)
        # if direction_str_term is None:
        #     continue
        parent = term_collection.find_term_by_code(item.parent_statement_code)
        child = parent.create_child_term(item.statement_content, code=item.statement_code)
        term_collection.append(child)


# ##################### load entity term ############################

data = auto_load_table_from_sql(base_data_dir, 'knowsys_', 'ks_system_entity',
                                LOAD_FROM_SQL, 'knowsys_',
                                converters={'category_code': str, 'entity_code': str, 'parent_entity_code': str})
# data = data[(data["del_stat"] == 0)]
data = data[(data['version_name'] == 'Standard')]
l1_data = data[data['parent_entity_code'] == '0000000000']
for item in l1_data.iloc:
    parent = term_collection.find_term_by_code(code=item.category_code)
    child = parent.create_term(item.entity_name, item.entity_code)
    term_collection.append(child)

other_data = data[(data['parent_entity_code'] != '0000000000') & (data['parent_entity_code'] != '/')]
for item in other_data.iloc:
    parent = term_collection.find_term_by_code(code=item.parent_entity_code)
    if parent is None:
        continue
    child = parent.create_child_term(item.entity_name, item.entity_code)
    term_collection.append(child)


# ##################### load property ############################


data = auto_load_table_from_sql(base_data_dir, 'knowsys_', 'ks_system_property',
                                LOAD_FROM_SQL, 'knowsys_',
                                converters={'category_code': str, 'entity_code': str, 'parent_entity_code': str})

# data = data[(data["del_stat"] == 0)]

for item in data.iloc:
    parent = term_collection.find_term_by_code(code=item.category_code)
    if parent is None:
        continue
    if isinstance(item.attributes, str):
        attrs = [i.strip() for i in item.attributes.split(',')]
    else:
        attrs = item.attributes if not np.isnan(item.attributes) else []
    prop = parent.create_property(item.property_name_cn, item.property_code, None, item.property_name, item.attributes)
    term_collection.append(prop)


# ##################### load property term ############################


data = auto_load_table_from_sql(base_data_dir, 'knowsys_', 'ks_system_property_expression',
                                LOAD_FROM_SQL, 'knowsys_',
                                converters={'category_code': str, 'property_code': str,
                                            'parent_expression_code': str, 'expression_code': str})
# data = data[(data["del_stat"] == 0)]
data = data[(data['expression_level'] == 1)]

l1_data = data[data['parent_expression_code'] == data['property_code']]
for item in l1_data.iloc:
    parent = term_collection.find_term_by_code(code=item.property_code)
    if parent is None:
        # print(f'cannot found property: {item.property_code}')
        continue
    if not isinstance(parent, Property):
        # print(f'{item.property_code} is not a property')
        continue
    new_prop = parent.create_child(item.expression_content, item.expression_code)
    term_collection.append(new_prop)

other_data = data[data['parent_expression_code'] != data['property_code']]
for item in other_data.iloc:
    parent = term_collection.find_term_by_code(code=item.property_code)
    if parent is None:
        # print(f'cannot found property: {item.property_code}')
        continue
    if not isinstance(parent, Property):
        print(f'{item.property_code} is not a property')
        continue
    new_prop = parent.create_child(item.expression_content, item.expression_code)
    term_collection.append(new_prop)


__knowsys_version__ = 1

__all__ = ['root', 'entity_root', 'relation_root', '__knowsys_version__']


########## checking ###############


for relation_meta in relation_root:
    for relation in relation_meta:
        all_term_length = len(relation.terms_with_children)
        if all_term_length == 0:
            logging.warning(f'[knowsys_]: relation: `{relation}` have no terms.')
