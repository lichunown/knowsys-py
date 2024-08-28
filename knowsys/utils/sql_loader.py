import os

import MySQLdb
import pandas as pd
from sshtunnel import SSHTunnelForwarder

from typing import *


SQL_ENV = os.environ.get('LOAD_FROM_SQL', 'knowsys-pre')


def load_table_from_sql_vanilla(db_name: str, sql: str):
    # with SSHTunnelForwarder(
    #         (ssh_host, ssh_port),  # B机器的配置--跳板机
    #         ssh_password=ssh_passwd,  # B机器的配置--跳板机账号
    #         ssh_username=ssh_username,  # B机器的配置--跳板机账户密码
    #         remote_bind_address=(mysql_host, mysql_port)) as server:  # A机器的配置-MySQL服务器

    conn = MySQLdb.connect(host=mysql_host,  # 此处必须是必须是127.0.0.1，代表C机器
                           port=mysql_port,
                           user=mysql_username,  # A机器的配置-MySQL服务器账户
                           passwd=mysql_passwd,  # A机器的配置-MySQL服务器密码c
                           db=db_name,  # 可以限定，只访问特定的数据库,否则需要在mysql的查询或者操作语句中，指定好表名
                           charset='utf8'  # 和数据库字符编码集合，保持一致，这样能够解决读出数据的中文乱码问题
                           )
    data = pd.read_sql(sql, conn)
    return data


def load_tables_from_sql(db_name: str, table_names: List[str]) -> List[pd.DataFrame]:
    # with SSHTunnelForwarder(
    #         (ssh_host, ssh_port),  # B机器的配置--跳板机
    #         ssh_password=ssh_passwd,  # B机器的配置--跳板机账号
    #         ssh_username=ssh_username,  # B机器的配置--跳板机账户密码
    #         remote_bind_address=(mysql_host, mysql_port)) as server:  # A机器的配置-MySQL服务器

    conn = MySQLdb.connect(host=mysql_host,  # 此处必须是必须是127.0.0.1，代表C机器
                           port=mysql_port,
                           user=mysql_username,  # A机器的配置-MySQL服务器账户
                           passwd=mysql_passwd,  # A机器的配置-MySQL服务器密码c
                           db=db_name,  # 可以限定，只访问特定的数据库,否则需要在mysql的查询或者操作语句中，指定好表名
                           charset='utf8'  # 和数据库字符编码集合，保持一致，这样能够解决读出数据的中文乱码问题
                           )
    res = []
    for name in table_names:
        data = pd.read_sql(f'select * from {name}', conn)
        res.append(data)

    return res


def load_table_from_sql(db_name: str, table_name: str) -> pd.DataFrame:
    return load_tables_from_sql(db_name, [table_name])[0]


def save_tables_from_sql(to_dir: str, db_name: str, table_names: List[str]):
    tables: List[pd.DataFrame] = load_tables_from_sql(db_name, table_names)

    if not os.path.exists(to_dir):
        os.makedirs(to_dir)

    for name, table in zip(table_names, tables):
        table.to_excel(os.path.join(to_dir, name + '.xlsx'))


def auto_load_table_from_sql(cached_dir, db_name, table_name, force_update=False,
                             prefix: str = "", **kwargs) -> pd.DataFrame:
    excel_data_path = os.path.join(cached_dir, table_name + '.xlsx')

    if not os.path.exists(excel_data_path):
        force_update = True

    if force_update:
        print(f'[{prefix}]: Loading {table_name} from sql ...')
        save_tables_from_sql(cached_dir, db_name, [table_name])
        print(f'[{prefix}]: Load {table_name} finished.')

    print(f'[{prefix}]: Load {table_name} from `{excel_data_path}`')
    return pd.read_excel(excel_data_path, **kwargs)


def auto_load_table_from_sql_vanilla(cached_dir, db_name: str, sql: str, save_name=None,
                                     force_update=False, prefix: str = "", **kwargs) -> pd.DataFrame:
    if save_name is not None:
        excel_data_path = os.path.join(cached_dir, save_name + '.xlsx')
    else:
        excel_data_path = None

    if excel_data_path is None or not os.path.exists(excel_data_path):
        force_update = True

    if force_update:
        print(f'[{prefix}]: exec {sql} from sql ...')
        data = load_table_from_sql_vanilla(db_name, sql)
        if excel_data_path is not None:
            data.to_excel(excel_data_path)
            print(f'[{prefix}]: saving data to {excel_data_path} finished.')
    else:
        data = pd.read_excel(excel_data_path, **kwargs)
        print(f'[{prefix}]: loading data from {excel_data_path} finished.')

    return data

