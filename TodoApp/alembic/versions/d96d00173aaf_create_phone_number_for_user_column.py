"""Create phone_number for user column

Revision ID: d96d00173aaf
Revises: 
Create Date: 2026-02-18 14:24:12.760812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd96d00173aaf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',sa.Column('phone_number',sa.String(),nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users','phone_number')
