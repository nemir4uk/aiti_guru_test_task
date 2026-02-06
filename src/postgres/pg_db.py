import datetime
import os
import enum
from typing import List
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import BigInteger, Identity, ForeignKey, Integer, DateTime, UniqueConstraint, func, Enum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY

load_dotenv(find_dotenv())

engine = create_async_engine(os.getenv('PG_DB_URL'))  #, echo=True)

AsyncSessionMain = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session():
    async with AsyncSessionMain() as async_session:
        yield async_session


class OrderStatus(enum.Enum):
    in_cart = "in_cart"
    payment_pending = "payment_pending_order"
    proccesed = "proccesed_orders"
    delivered = "delivered_orders"
    canceled = "canceled_orders"


class PgBase(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)


class Categories(PgBase):
    __tablename__ = 'categories'

    category_name: Mapped[str]
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id', ondelete='SET NULL'))
    categorypath: Mapped[List[int]] = mapped_column(ARRAY(Integer))


class Products(PgBase):
    __tablename__ = 'products'

    product_name: Mapped[str]
    price: Mapped[float]
    quantity: Mapped[int]
    category_id: Mapped[int] = mapped_column((ForeignKey('categories.id', ondelete="RESTRICT")))


class Clients(PgBase):
    __tablename__ = 'clients'

    client_name: Mapped[str]
    address: Mapped[str]


class OrderItems(PgBase):
    __tablename__ = 'order_items'

    order_id: Mapped[int]
    client_id: Mapped[int]
    created_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int]
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus))

    __table_args__ = (UniqueConstraint("order_id", "product_id"),)


class ConfirmedOrders(PgBase):
    __tablename__ = 'confirmed_orders'

    client_id: Mapped[int]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    order_id: Mapped[int]
    product_id: Mapped[int]
    quantity: Mapped[int]
