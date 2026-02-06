import os
import time
from dotenv import load_dotenv, find_dotenv
from clickhouse_sqlalchemy import make_session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from faker import Faker
import numpy as np
import matplotlib.pyplot as plt

load_dotenv(find_dotenv())

ch_list = [os.getenv('CH_DB_URL_1'), os.getenv('CH_DB_URL_2'), os.getenv('CH_DB_URL_3'), os.getenv('CH_DB_URL_4')]
engine_pg = create_engine(os.getenv('PG_SYNC_URL'), echo=False)
Session_pg = sessionmaker(bind=engine_pg)


def insert_objects(sync_session, statement) -> None:
    with sync_session() as session:
        session.execute(statement)
        session.commit()


def make_request(sync_session, statement) -> None:
    with sync_session() as session:
        t0 = time.perf_counter()
        req = session.execute(statement)
        res = req.fetchall()
        time_dict['Postgres'].append(time.perf_counter() - t0)


Faker.seed(4321)
np.random.seed(1234)
fake = Faker('ru_RU')

year_days = 365
mean_sales = 50000
standard_deviation_sales = 5000  # guess
normal_data = np.random.normal(mean_sales, standard_deviation_sales, year_days)
daily_sales = list(map(int, normal_data))
select_query = """select sum(quantity) as top_5, product_id 
        from confirmed_orders
        where created_at > (NOW() - INTERVAL '1 month')
        group by product_id
        order by top_5 desc
        limit 5"""

time_dict_keys = ch_list + ['Postgres']
time_dict = {key: [] for key in time_dict_keys}
order_id_counter = 0
for current_day in range(year_days):
    exponential_data = np.random.exponential(scale=20.0, size=daily_sales[current_day]) + 0.5
    quantity_of_products = list(map(round, exponential_data))
    days_gap = year_days - current_day
    stmt = text(f"""insert into confirmed_orders (order_id, client_id, product_id, quantity, created_at)
    values {','.join([f'''({current_day}, {np.random.randint(20)}, {np.random.randint(50)}, 
    {quantity_of_products[order]}, '{fake.date_time_between(f'-{days_gap}d', f'-{days_gap-1}d')}') ''' 
                      for order in range(daily_sales[current_day])])}""")

    for env in ch_list:
        Session_ch = make_session(create_engine(env))
        with Session_ch as ch_session:
            ch_session.execute(stmt)
            ch_session.commit()

    insert_objects(Session_pg, stmt)
    order_id_counter += 1

    for env in ch_list:
        Session_ch = make_session(create_engine(env))
        with Session_ch as ch_session:
            t0 = time.perf_counter()
            ch_session.execute(text(select_query))
            time_dict[env].append(time.perf_counter() - t0)

    make_request(Session_pg, text(select_query))
    time.sleep(2)
    print(current_day)


print(time_dict)

plt.plot(time_dict['Postgres'], color='blue', label='Postgres')
ch_colors = iter(['#e5ed47', '#c2c93c', '#91962d', '#767a1a'])
ch_configs = iter(['cpu-1_2g', 'cpu-2_4g', 'cpu-4_8g', 'cpu-4_16g'])
for ch in ch_list:
    plt.plot(time_dict[ch], color=next(ch_colors), label=next(ch_configs))
plt.ylim(0, 3)
plt.xlabel('Days')
plt.ylabel('Time')
plt.legend()
plt.show()
