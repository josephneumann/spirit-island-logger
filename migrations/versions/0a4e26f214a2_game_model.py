"""
Spirit Island - Alembic Migration
Copyright (c) 2020 by Joseph Neumann.  All rights reserved.
This file is part of an open-source game logger and randomizer for the tabletop game
`Spirit Island` and its expansions.  No claim is made to the rights of the `Spirit Island` content
which is owned by  `Greater Than Games`
The project is released under the MIT License Agreement.  See the LICENSE.txt file included in the package
Initial implementation of Game data model

Revision ID: 0a4e26f214a2
Revises: 800c506d53e4
Create Date: 2020-04-17 22:18:01.880918

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a4e26f214a2'
down_revision = '800c506d53e4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('game',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('player_count', sa.Integer(), nullable=True),
    sa.Column('adversary_level_id', sa.Text(), nullable=True),
    sa.Column('scenario_id', sa.Text(), nullable=True),
    sa.Column('difficulty', sa.Integer(), nullable=True),
    sa.Column('handicap', sa.Integer(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('is_complete', sa.Boolean(), nullable=False),
    sa.Column('is_victory', sa.Boolean(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['adversary_level_id'], ['adversary_level.id'], ),
    sa.ForeignKeyConstraint(['scenario_id'], ['scenario.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game_board',
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('board_id', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['board_id'], ['board.id'], ),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], )
    )
    op.create_table('game_expansion',
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('expansion_id', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['expansion_id'], ['expansion.id'], ),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], )
    )
    op.create_table('spirit_game_play',
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('spirit_id', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.ForeignKeyConstraint(['spirit_id'], ['spirit.id'], )
    )


def downgrade():
    op.drop_table('spirit_game_play')
    op.drop_table('game_expansion')
    op.drop_table('game_board')
    op.drop_table('game')
