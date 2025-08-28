"""merge heads

Revision ID: 3aa45e97cb8f
Revises: 05dc8a1bf552, e50ed6d8c309
Create Date: 2025-08-28 16:47:42.482052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3aa45e97cb8f'
down_revision: Union[str, None] = ('05dc8a1bf552', 'e50ed6d8c309')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
