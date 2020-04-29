"""Seed data

Revision ID: c6c5149852f8
Revises: 4f38526256fd
Create Date: 2020-04-28 23:15:26.850215

"""
from alembic import op
import sqlalchemy as sa
from seed import seed_game_data, seed_admin_user


# revision identifiers, used by Alembic.
revision = 'c6c5149852f8'
down_revision = '4f38526256fd'
branch_labels = None
depends_on = None


def upgrade():
    seed_game_data()
    seed_admin_user()

def downgrade():
    pass
