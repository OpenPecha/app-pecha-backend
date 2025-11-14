"""added_display_order_in_user_recitation_table

Revision ID: 070d63ce5dcc
Revises: 77f12151114b
Create Date: 2025-11-15 01:35:43.100196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '070d63ce5dcc'
down_revision: Union[str, None] = '77f12151114b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add display_order column to user_recitations table
    # First add as nullable to allow existing rows
    op.add_column('user_recitations', sa.Column('display_order', sa.Integer(), nullable=True))
    
    # Update existing rows with sequential display_order values per user
    op.execute("""
        WITH numbered_recitations AS (
            SELECT id, 
                   ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY id) as row_num
            FROM user_recitations
        )
        UPDATE user_recitations
        SET display_order = numbered_recitations.row_num
        FROM numbered_recitations
        WHERE user_recitations.id = numbered_recitations.id
    """)
    
    # Now make the column NOT NULL
    op.alter_column('user_recitations', 'display_order', nullable=False)


def downgrade() -> None:
    # Remove display_order column
    op.drop_column('user_recitations', 'display_order')
