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
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Game, Spirit, Board, AdversaryLevel, Scenario, Expansion, User
from app.forms import (
    CreateGameForm,
    EditGameForm,
    ScoreGameForm,
    RandomizeGameForm,
    SpiritCreateGameForm,
    LoginForm,
    DeleteGameForm
)
import itertools
from sqlalchemy.sql.functions import func


def chunked_iterable(iterable, size):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
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

    return render_template("index.html", title="Spirit Island", games=games, form=form)


@app.route("/games")
@login_required
def games():
    games = Game.query.order_by(Game.id.desc()).all()
    return render_template("games.html", title="Spirit Island - Games", games=games)


@app.route("/games/<game_id>/edit", methods=["GET", "POST"])
@login_required
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
    return render_template(
        "edit_game.html", title="Spirit Island - Edit Game", game=gm, form=form
    )


@app.route("/games/<game_id>/score", methods=["GET", "POST"])
@login_required
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
    return render_template(
        "score_game.html", title="Spirit Island - Score Game", game=gm, form=form
    )


@app.route("/games/<game_id>/randomize", methods=["GET", "POST"])
@login_required
def randomize_game(game_id):
    gm = Game.query.get_or_404(game_id)
    form = RandomizeGameForm()
    form.spirit_max_complexity.choices = [
        ("1", "Low"),
        ("2", "Moderate"),
        ("3", "High"),
        ("4", "Very High"),
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
        "randomize_game.html", title="Spirit Island -Randomize Game", game=gm, form=form
    )


@app.route("/spirits")
@login_required
def spirits():
    spirits = chunked_iterable(
        Spirit.query.order_by(Spirit.name).all(), 3
    )  # This is a generator
    return render_template(
        "spirits.html", title="Spirit Island - Spirits", chunked_spirits=spirits
    )


@app.route("/spirits/<spirit_id>")
@login_required
def spirit(spirit_id):
    spirit = Spirit.query.get_or_404(spirit_id)
    games = spirit.games
    return render_template(
        "spirit.html",
        title="Spirit Island - {}".format(spirit.name),
        spirit=spirit,
        games=games,
    )


@app.route("/spirits/<spirit_id>/create_game", methods=["GET", "POST"])
@login_required
def spirit_create_game(spirit_id):
    form = SpiritCreateGameForm()
    form.expansions.choices = [
        (e.id, e.name) for e in Expansion.query.filter(Expansion.id != "base").all()
    ]
    form.players.choices = [(str(x), str(x)) for x in range(1, 5)]
    form.spirits.choices = [(s.id, s.name) for s in Spirit.query.all()]
    if form.validate_on_submit():
        new_game = Game(
            player_count=int(form.data.get("players")), expansions=form.expansions.data
        )
        new_game.spirits = [Spirit.query.get(s) for s in form.spirits.data]
        db.session.add(new_game)
        db.session.commit()
        return redirect(url_for("edit_game", game_id=new_game.id))
    elif request.method == "GET":
        form.spirits.data = spirit_id
    for error in form.errors:
        flash("{}: {}".format(error.capitalize(), form.errors[error][0]), "danger")

    return render_template(
        "spirit_create_game.html", title="Spirit Island - Create Game", form=form
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("index"))
    return render_template("login.html", title="Spirit Island - Log In", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/games/<game_id>/delete", methods=["GET","POST"])
@login_required
def delete_game(game_id):
    g = Game.query.get_or_404(game_id)
    form = DeleteGameForm()
    if form.validate_on_submit():
        if not form.confirm_text.data == str(g.id):
            flash("Cofirmation text did not match.", "danger")
            # return redirect(url_for("delete_game", game_id=game_id))
        else:
            db.session.delete(g)
            db.session.commit()
            flash ("Game deleted successfully.", "success")
            return redirect(url_for("index"))
    return render_template("delete_game.html", game=g, form=form)

