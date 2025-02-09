"""empty message

Revision ID: f6722f4e0490
Revises: 05dc8a1bf552, e50ed6d8c309
Create Date: 2025-02-04 07:57:44.773686

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6722f4e0490'
down_revision: Union[str, None] = ('05dc8a1bf552', 'e50ed6d8c309')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
