"""
Spirit Island - Alembic Migration
Copyright (c) 2020 by Joseph Neumann.  All rights reserved.
This file is part of an open-source game logger and randomizer for the tabletop game
`Spirit Island` and its expansions.  No claim is made to the rights of the `Spirit Island` content
which is owned by  `Greater Than Games`
The project is released under the MIT License Agreement.  See the LICENSE.txt file included in the package

Initial Expansion, Spirit, Adversary, Scenario, Board models

Revision ID: 800c506d53e4
Revises: 
Create Date: 2020-04-17 21:43:53.247368

"""
from alembic import op
import sqlalchemy as sa
from seed import seed_game_data


# revision identifiers, used by Alembic.
revision = "800c506d53e4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "expansion",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("blight_cards", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "adversary",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("additional_loss_condition", sa.Text(), nullable=True),
        sa.Column("escalation", sa.Text(), nullable=True),
        sa.Column("expansion_id", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["expansion_id"], ["expansion.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "board",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("is_thematic", sa.Boolean(), nullable=False),
        sa.Column("expansion_id", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["expansion_id"], ["expansion.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "scenario",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.Integer(), nullable=True),
        sa.Column("expansion_id", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["expansion_id"], ["expansion.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "spirit",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("complexity", sa.Integer(), nullable=True),
        sa.Column("setup", sa.Text(), nullable=True),
        sa.Column("offense", sa.Integer(), nullable=True),
        sa.Column("control", sa.Integer(), nullable=True),
        sa.Column("fear", sa.Integer(), nullable=True),
        sa.Column("defense", sa.Integer(), nullable=True),
        sa.Column("utility", sa.Integer(), nullable=True),
        sa.Column("expansion_id", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["expansion_id"], ["expansion.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "adversary_level",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("adversary_id", sa.Text(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.Integer(), nullable=True),
        sa.Column("level_one_fear", sa.Integer(), nullable=True),
        sa.Column("level_two_fear", sa.Integer(), nullable=True),
        sa.Column("level_three_fear", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["adversary_id"], ["adversary.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "scenario_adversary_handicap",
        sa.Column("scenario_id", sa.Text(), nullable=False),
        sa.Column("adversary_id", sa.Text(), nullable=False),
        sa.Column("handicap", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["adversary_id"], ["adversary.id"],),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenario.id"],),
        sa.PrimaryKeyConstraint("scenario_id", "adversary_id"),
    )
    op.create_table(
        "spirit_adversary_handicap",
        sa.Column("spirit_id", sa.Text(), nullable=False),
        sa.Column("adversary_id", sa.Text(), nullable=False),
        sa.Column("handicap", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["adversary_id"], ["adversary.id"],),
        sa.ForeignKeyConstraint(["spirit_id"], ["spirit.id"],),
        sa.PrimaryKeyConstraint("spirit_id", "adversary_id"),
    )
    op.create_table(
        "spirit_scenario_handicap",
        sa.Column("spirit_id", sa.Text(), nullable=False),
        sa.Column("scenario_id", sa.Text(), nullable=False),
        sa.Column("handicap", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenario.id"],),
        sa.ForeignKeyConstraint(["spirit_id"], ["spirit.id"],),
        sa.PrimaryKeyConstraint("spirit_id", "scenario_id"),
    )

    # Seed data
    seed_game_data()


def downgrade():
    op.drop_table("spirit_scenario_handicap")
    op.drop_table("spirit_adversary_handicap")
    op.drop_table("scenario_adversary_handicap")
    op.drop_table("adversary_level")
    op.drop_table("spirit")
    op.drop_table("scenario")
    op.drop_table("board")
    op.drop_table("adversary")
    op.drop_table("expansion")
