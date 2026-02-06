import os
import datetime
from dotenv import load_dotenv, find_dotenv
from clickhouse_sqlalchemy import make_session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from faker import Faker
import numpy as np
import matplotlib.pyplot as plt

load_dotenv(find_dotenv())
fake = Faker('ru_RU')

ch_list = [os.getenv('CH_DB_URL_1'), os.getenv('CH_DB_URL_2'), os.getenv('CH_DB_URL_3'), os.getenv('CH_DB_URL_4')]
engine_pg = create_engine(os.getenv('PG_SYNC_URL'), echo=False)
Session_pg = sessionmaker(bind=engine_pg)

# ch_statement = f"""insert into  confirmed_orders (order_id, client_id, product_id, quantity, created_at)
#     values (1,1,1,1,'{fake.date_time_between(f'-2d', f'-1d')}')"""
ch_statement = """ALTER TABLE confirmed_orders DELETE where 1=1"""
pg_statement = """delete from confirmed_orders """


def clear_db_ch(sync_session, statement) -> None:
    with sync_session as session:
        session.execute(statement)
        session.commit()


def clear_db_pg(sync_session, statement) -> None:
    with sync_session() as session:
        session.execute(statement)
        session.commit()


clear_db_pg(Session_pg, text(pg_statement))

for env in ch_list:
    Session_ch = make_session(create_engine(env))
    clear_db_ch(Session_ch, text(ch_statement))

