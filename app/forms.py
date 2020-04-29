"""
Spirit Island - Forms
Copyright (c) 2020 by Joseph Neumann.  All rights reserved.
This file is part of an open-source game logger and randomizer for the tabletop game
`Spirit Island` and its expansions.  No claim is made to the rights of the `Spirit Island` content
which is owned by  `Greater Than Games`
The project is released under the MIT License Agreement.  See the LICENSE.txt file included in the package
"""
# Copyright 2018 by Peter Cock, The James Hutton Institute.
# All rights reserved.
# This file is part of the THAPBI Phytophthora ITS1 Classifier Tool (PICT),
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
from flask_wtf import FlaskForm
from wtforms import (
    ValidationError,
    BooleanField,
    IntegerField,
    SubmitField,
    DateField,
    SelectMultipleField,
    SelectField,
    TextAreaField,
    PasswordField,
    StringField,
)
from wtforms.validators import DataRequired, NumberRange, Optional


class CreateGameForm(FlaskForm):
    players = SelectField("Players", validators=[DataRequired()])
    expansions = SelectMultipleField("Expansions")
    create_game = SubmitField("Create Game")


def validate_spirit_count(form, field):
    if field.data and len(field.data) != form.players.data:
        raise ValidationError("Number of Spirits selected does not match player count")


def validate_board_count(form, field):
    if field.data and len(field.data) != form.players.data:
        raise ValidationError("Number of Boards selected does not match player count")


class SpiritCreateGameForm(FlaskForm):
    players = SelectField("Players", validators=[DataRequired()])
    spirits = SelectMultipleField("Spirits")
    expansions = SelectMultipleField("Expansions")
    create_game = SubmitField("Create Game")


class EditGameForm(FlaskForm):
    players = IntegerField(
        "Players",
        validators=[
            DataRequired(),
            NumberRange(min=1, max=4, message="Must be 1-4 players"),
        ],
    )
    update_game = SubmitField("Save Game")
    date = DateField("Date")
    spirits = SelectMultipleField("Spirits", validators=[validate_spirit_count])
    boards = SelectMultipleField("Boards", validators=[validate_board_count])
    scenario = SelectField("Scenario")
    adversary = SelectField("Adversary")
    status = SelectField("Status")
    rating = IntegerField(
        "Rating (1-10)", validators=[Optional(), NumberRange(min=0, max=10)]
    )
    notes = TextAreaField("Notes")


class ScoreGameForm(FlaskForm):
    outcome = SelectField("Outcome")
    invader_cards = IntegerField(
        "Invader Cards in Deck", validators=[DataRequired(), NumberRange(min=0, max=12)]
    )
    dahan = IntegerField(
        "Dahan Left", validators=[DataRequired(), NumberRange(min=0, max=50)]
    )
    blight = IntegerField(
        "Blight", validators=[DataRequired(), NumberRange(min=0, max=50)]
    )
    score_game = SubmitField("Calculate Score")


class RandomizeGameForm(FlaskForm):
    use_thematic_boards = BooleanField("Thematic")
    spirit_max_complexity = SelectField("Max Spirit Complexity")
    use_scenario = BooleanField("Use Scenario")
    scenario_max_difficulty = SelectField(
        "Scenario Max Difficulty", validators=[Optional()]
    )
    use_adversary = BooleanField("Use Adversary")
    adversary_max_difficulty = SelectField(
        "Adversary Max Difficulty", validators=[Optional()]
    )
    force = BooleanField("Force Over-write")
    randomize = SubmitField("Randomize Game")


class LoginForm(FlaskForm):
    username = StringField("Username")
    password = PasswordField("Password")
    remember_me = BooleanField("Remember Me")
    login = SubmitField("Log In")
