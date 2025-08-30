"""add_plan_related_tables

Revision ID: e86de3ca779a
Revises: 3aa45e97cb8f
Create Date: 2025-08-28 16:50:40.246842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e86de3ca779a'
down_revision: Union[str, None] = '3aa45e97cb8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This revision intentionally contains no schema changes.
    pass


def downgrade() -> None:
    # This revision intentionally contains no schema changes.
    pass

