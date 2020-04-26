"""
Spirit Island - Routes
Copyright (c) 2020 by Joseph Neumann.  All rights reserved.
This file is part of an open-source game logger and randomizer for the tabletop game
`Spirit Island` and its expansions.  No claim is made to the rights of the `Spirit Island` content
which is owned by  `Greater Than Games`
The project is released under the MIT License Agreement.  See the LICENSE.txt file included in the package
"""
from app import app, db
from flask import render_template, url_for, redirect, request, flash
from app.models import Game, Spirit, Board, AdversaryLevel, Scenario, Expansion
from app.forms import CreateGameForm, EditGameForm, ScoreGameForm, RandomizeGameForm
import itertools


def chunked_iterable(iterable, size):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    games = Game.query.order_by(Game.date.desc()).limit(
        5
    )  # Only Retrieve Latest 5 Games
    form = CreateGameForm()
    form.expansions.choices = [
        (e.id, e.name) for e in Expansion.query.filter(Expansion.id != "base").all()
    ]
    form.players.choices = [(str(x), str(x)) for x in range(1, 5)]
    if form.validate_on_submit():
        new_game = Game(
            player_count=int(form.data.get("players")), expansions=form.expansions.data
        )
        db.session.add(new_game)
        db.session.commit()
        return redirect(url_for("edit_game", game_id=new_game.id))
    for error in form.errors:
        flash("{}: {}".format(error.capitalize(), form.errors[error][0]), "danger")

    return render_template("index.html", title="Home", games=games, form=form)


@app.route("/games")
def games():
    games = Game.query.order_by(Game.id.desc()).all()
    return render_template("games.html", title="Games", games=games)


@app.route("/spirits")
def spirits():
    spirits = chunked_iterable(Spirit.query.order_by(Spirit.name).all(), 3)  # This is a generator
    return render_template("spirits.html", title="Spirits", chunked_spirits=spirits)


@app.route("/games/<game_id>/edit", methods=["GET", "POST"])
def edit_game(game_id):
    form = EditGameForm()
    gm = Game.query.get_or_404(game_id)
    form.spirits.choices = [(s.id, s.name) for s in gm.get_all_expansion_spirits()]
    form.boards.choices = [(b.id, b.id) for b in Board.query.all()]
    none_tuple = ("None", "None")
    scn_choices = [
        (s.id, "{} (Difficulty: {})".format(s.name, s.difficulty))
        for s in gm.get_available_scenarios(10)
    ]
    scn_choices.insert(0, none_tuple)
    form.scenario.choices = scn_choices
    adversary_choices = [
        (
            a.id,
            "{} lvl:{} (difficulty {})".format(a.adversary.name, a.level, a.difficulty),
        )
        for a in gm.get_available_adversary_levels(10)
    ]
    adversary_choices.insert(0, none_tuple)
    form.adversary.choices = adversary_choices
    form.status.choices = [(x, x) for x in ["Incomplete", "Victory", "Defeat"]]

    if form.validate_on_submit():
        gm.player_count = form.players.data
        gm.date = form.date.data
        # Handle spirits
        gm.spirits = [Spirit.query.get(s) for s in form.spirits.data]
        # Handle boards
        gm.boards = [Board.query.get(b) for b in form.boards.data]
        # Scenario
        gm.scenario = (
            Scenario.query.get(form.scenario.data)
            if form.scenario.data != "None"
            else None
        )
        # Adversary
        gm.adversary_level = (
            AdversaryLevel.query.get(form.adversary.data)
            if form.adversary.data != "None"
            else None
        )
        # Re-Calculate
        gm.calculate_difficulty()
        gm.calculate_handicap()

        # Update game statuses
        if form.status.data == "Incomplete":
            gm.is_complete = False
            gm.score = 0
        else:
            gm.is_complete = True
        if form.status.data == "Victory":
            gm.is_victory = True
        if form.status.data == "Defeat":
            gm.is_victory = False

        # Get rating data
        gm.rating = form.rating.data
        gm.notes = form.notes.data

        db.session.add(gm)
        db.session.commit()
        flash("Game updated!", "success")
        return redirect(url_for("edit_game", game_id=gm.id))
    elif request.method == "GET":
        # Populate Edit Game Form
        form.players.data = gm.player_count
        form.date.data = gm.date
        form.spirits.data = [s.id for s in gm.spirits]
        form.boards.data = [b.id for b in gm.boards]
        form.scenario.data = gm.scenario.id if gm.scenario is not None else None
        form.adversary.data = (
            gm.adversary_level.id if gm.adversary_level is not None else None
        )
        form.status.data = gm.status
        form.rating.data = gm.rating
        form.notes.data = gm.notes

    for error in form.errors:
        flash("{}: {}".format(error.capitalize(), form.errors[error][0]), "danger")
    return render_template("edit_game.html", title="Edit Game", game=gm, form=form)


@app.route("/games/<game_id>/score", methods=["GET", "POST"])
def score_game(game_id):
    form = ScoreGameForm()
    gm = Game.query.get_or_404(game_id)
    form.outcome.choices = [(x, x) for x in ["Victory", "Defeat"]]

    if form.validate_on_submit():
        gm.is_complete = True
        if form.outcome.data == "Victory":
            gm.is_victory = True
        else:
            gm.is_victory = False
        gm.calculate_score(
            victory=gm.is_victory,
            invader_cards_in_deck=form.invader_cards.data,
            dahan=form.dahan.data,
            blight=form.blight.data,
        )
        db.session.add(gm)
        db.session.commit()

        flash("Game score: {}".format(gm.score), "success")
        return redirect(url_for("edit_game", game_id=gm.id))
    for error in form.errors:
        flash("{}: {}".format(error.capitalize(), form.errors[error][0]), "danger")
    return render_template("score_game.html", title="Score Game", game=gm, form=form)


@app.route("/games/<game_id>/delete")
def delete_game(game_id):
    db.session.delete(Game.query.get_or_404(game_id))
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/games/<game_id>/randomize", methods=["GET", "POST"])
def randomize_game(game_id):
    gm = Game.query.get_or_404(game_id)
    form = RandomizeGameForm()
    form.spirit_max_complexity.choices = [
        ("1", "Low"),
        ("2", "Moderate"),
        ("3", "High"),
    ]
    form.scenario_max_difficulty.choices = [(str(x), x) for x in range(5)]
    form.adversary_max_difficulty.choices = [(str(x), x) for x in range(11)]
    if form.validate_on_submit():
        gm.randomize(
            use_thematic_boards=form.use_thematic_boards.data,
            spirit_max_complexity=int(form.spirit_max_complexity.data),
            scenario_max_difficulty=int(form.scenario_max_difficulty.data)
            if form.use_scenario.data
            else None,
            adversary_max_difficulty=int(form.adversary_max_difficulty.data)
            if form.use_adversary.data
            else None,
            force=form.force.data,
        )
        db.session.add(gm)
        db.session.commit()
        if form.force.data:
            flash(
                "Game randomized - existing game configuration overwritten", "success"
            )
        else:
            flash("Game randomized - existing game configuration conserved", "success")
        return redirect(url_for("edit_game", game_id=gm.id))
    elif request.method == "GET":
        form.use_thematic_boards.data = gm.is_thematic if gm.boards else True
        form.spirit_max_complexity.data = "3"
        form.use_scenario.data = False
        form.scenario_max_difficulty.data = "4"
        form.use_adversary.data = False
        form.adversary_max_difficulty.data = "10"
    for error in form.errors:
        flash("{}: {}".format(error.capitalize(), form.errors[error][0]), "danger")
    return render_template(
        "randomize_game.html", title="Randomize Game", game=gm, form=form
    )
