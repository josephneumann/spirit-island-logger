"""Add color to Spirit model

Revision ID: 491f46f9e760
Revises: 0a4e26f214a2
Create Date: 2020-04-25 22:00:13.759921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '491f46f9e760'
down_revision = '0a4e26f214a2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('spirit', sa.Column('color', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('spirit', 'color')
