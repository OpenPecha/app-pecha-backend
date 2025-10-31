"""update planstatus enum: replace UNDER_REVIEW -> UNPUBLISHED; add DELETED

Revision ID: 38fe2996fa07
Revises: b070df8539e6
Create Date: 2025-10-31 12:22:12.309530

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38fe2996fa07'
down_revision: Union[str, None] = 'b070df8539e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # 1) Create the new enum type with the desired labels
    op.execute("CREATE TYPE planstatus_new AS ENUM ('DRAFT', 'PUBLISHED', 'UNPUBLISHED', 'ARCHIVED', 'DELETED')")

    # 2) Alter the column to use the new enum type, mapping old values inline
    op.execute(
        """
        ALTER TABLE plans
        ALTER COLUMN status TYPE planstatus_new
        USING (
            CASE status::text
                WHEN 'UNDER_REVIEW' THEN 'UNPUBLISHED'
                ELSE status::text
            END
        )::planstatus_new
        """
    )

    # 4) Drop old type and rename new type to the original name
    op.execute("DROP TYPE planstatus")
    op.execute("ALTER TYPE planstatus_new RENAME TO planstatus")


def downgrade() -> None:
    # Recreate the old enum type
    op.execute("CREATE TYPE planstatus_old AS ENUM ('DRAFT', 'PUBLISHED', 'ARCHIVED', 'UNDER_REVIEW')")

    # Switch the column back to the old type, mapping unsupported values inline
    op.execute(
        """
        ALTER TABLE plans
        ALTER COLUMN status TYPE planstatus_old
        USING (
            CASE status::text
                WHEN 'UNPUBLISHED' THEN 'UNDER_REVIEW'
                WHEN 'DELETED' THEN 'ARCHIVED'
                ELSE status::text
            END
        )::planstatus_old
        """
    )

    # Drop the current type and rename back
    op.execute("DROP TYPE planstatus")
    op.execute("ALTER TYPE planstatus_old RENAME TO planstatus")
