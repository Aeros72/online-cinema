"""add pending payment status

Revision ID: 8954fcfe0290
Revises: c6823f79d861
Create Date: 2026-06-02 10:40:21.444019

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8954fcfe0290'
down_revision: Union[str, Sequence[str], None] = 'c6823f79d861'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE paymentstatusenum ADD VALUE IF NOT EXISTS 'PENDING'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
