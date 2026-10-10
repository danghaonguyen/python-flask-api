"""Create tasks table

Revision ID: 09aa49b25b08
Revises: 
Create Date: 2026-10-09 15:54:31.572957

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '09aa49b25b08'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("tasks")

    # ### end Alembic commands ###
