"""create events table

Revision ID: 247a46e1c21c
Revises: 
Create Date: 2026-02-01 16:03:00.471417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '247a46e1c21c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(""" CREATE TABLE confirmed_orders
(
    order_id UInt64,
    client_id UInt64,
    product_id UInt64,
    quantity UInt32,
    created_at DateTime
)
ENGINE = SummingMergeTree
PARTITION BY toYYYYMM(created_at)
ORDER BY (product_id, created_at, order_id)
""")


def downgrade() -> None:
    op.execute("Drop table confirmed_orders")
