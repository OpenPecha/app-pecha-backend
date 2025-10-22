"""increase_image_url_column_size

Revision ID: a1b2c3d4e5f6
Revises: ed014f60334e
Create Date: 2025-09-13 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ed014f60334e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Increase image_url column size in plans table from VARCHAR(255) to VARCHAR(1000)
    op.alter_column('plans', 'image_url',
                   existing_type=sa.String(length=255),
                   type_=sa.String(length=1000),
                   existing_nullable=True)
    
    # Increase image_url column size in authors table from VARCHAR(255) to VARCHAR(1000)
    op.alter_column('authors', 'image_url',
                   existing_type=sa.String(length=255),
                   type_=sa.String(length=1000),
                   existing_nullable=True)


def downgrade() -> None:
    # Revert image_url column size in authors table back to VARCHAR(255)
    op.alter_column('authors', 'image_url',
                   existing_type=sa.String(length=1000),
                   type_=sa.String(length=255),
                   existing_nullable=True)
    
    # Revert image_url column size in plans table back to VARCHAR(255)
    op.alter_column('plans', 'image_url',
                   existing_type=sa.String(length=1000),
                   type_=sa.String(length=255),
                   existing_nullable=True)