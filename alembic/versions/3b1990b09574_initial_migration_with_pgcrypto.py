"""Initial migration with pgcrypto

Revision ID: 3b1990b09574
Revises:
Create Date: 2025-12-24 21:17:36.255349

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3b1990b09574"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pgcrypto extension for encryption
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop pgcrypto extension
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
