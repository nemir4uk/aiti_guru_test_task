import os
from clickhouse_sqlalchemy import engines
from sqlalchemy.engine.url import make_url

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def maybe_replicated(cluster, engine_name, table_name, *args, **kwargs):
    if cluster:
        engine_name = 'Replicated' + engine_name
        args = (make_replicated_zk_path(cluster, table_name), '{replica}') + args

    engine_cls = getattr(engines, engine_name)
    return engine_cls(*args, **kwargs)


def make_replicated_zk_path(cluster, table_name):
    database = make_url(os.getenv('CH_DB_URL_4')).database
    return f'/clickhouse/tables/{cluster}/{database}/{table_name}'


def maybe_replicated_engine_str(cluster, table_name, engine_str):
    if cluster:
        params_index = engine_str.index('(') + 1
        replicated_args = "'{}', '{{replica}}'".format(make_replicated_zk_path(cluster, table_name))
        if engine_str[params_index] != ')':
            replicated_args += ", "
        engine_str = 'Replicated' + (engine_str[:params_index] + replicated_args + engine_str[params_index:])

    return engine_str