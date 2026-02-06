import os
from dotenv import load_dotenv, find_dotenv
from clickhouse_sqlalchemy import make_session
from sqlalchemy import create_engine, BigInteger, Identity
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv(find_dotenv())


engine = create_engine(os.getenv('CH_DB_URL_4'))
Session = make_session(engine)


def get_session():
    with Session() as session:
        yield session


class ChBase(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

