"""seed user groups

Revision ID: 700d357be907
Revises: d08bedfea904
Create Date: 2026-04-24 17:37:41.621164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '700d357be907'
down_revision: Union[str, Sequence[str], None] = 'd08bedfea904'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO user_groups (name)
        VALUES ('USER'), ('MODERATOR'), ('ADMIN')
        ON CONFLICT (name) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM user_groups
        WHERE name IN ('USER', 'MODERATOR', 'ADMIN');
        """
    )
