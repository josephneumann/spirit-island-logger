"""
Spirit Island - Seed Utility
Copyright (c) 2020 by Joseph Neumann.  All rights reserved.
This file is part of an open-source game logger and randomizer for the tabletop game
`Spirit Island` and its expansions.  No claim is made to the rights of the `Spirit Island` content
which is owned by  `Greater Than Games`
The project is released under the MIT License Agreement.  See the LICENSE.txt file included in the package
"""
import json
from app import db
from app import app
from app.models import (
    Expansion,
    Spirit,
    Scenario,
    Adversary,
    AdversaryLevel,
    SpiritAdversaryHandicap,
    SpiritScenarioHandicap,
    ScenarioAdversaryHandicap,
    Board,
    User
)


def read_game_data():
    with open("game_data.json") as data_file:
        return json.load(data_file)


def seed_expansions(data):
    for exp in data:
        expansion = Expansion.query.get(exp) or Expansion()
        expansion.id = exp
        expansion.name = data[exp].get("name")
        expansion.blight_cards = data[exp].get("blight-cards") or 0
        db.session.add(expansion)


def seed_spirits(data):
    for exp in data:
        expansion = Expansion.query.get(exp)
        for sp in data[exp].get("spirits"):
            spirit = Spirit.query.get(sp) or Spirit()
            spirit.id = sp
            spirit.name = data[exp]["spirits"][sp].get("name")
            spirit.complexity = data[exp]["spirits"][sp].get("complexity")
            spirit.offense = data[exp]["spirits"][sp]["powers"].get("offense")
            spirit.control = data[exp]["spirits"][sp]["powers"].get("control")
            spirit.fear = data[exp]["spirits"][sp]["powers"].get("fear")
            spirit.defense = data[exp]["spirits"][sp]["powers"].get("defense")
            spirit.utility = data[exp]["spirits"][sp]["powers"].get("utility")
            spirit.setup = data[exp]["spirits"][sp].get("setup")
            spirit.color = data[exp]["spirits"][sp]["color"].get("background")
            expansion.spirits.append(spirit)
            db.session.add(spirit)


def seed_scenarios(data):
    for exp in data:
        expansion = Expansion.query.get(exp)
        for scn in data[exp].get("scenarios"):
            scenario = Scenario.query.get(scn) or Scenario()
            scenario.id = scn
            scenario.name = data[exp]["scenarios"][scn].get("name")
            scenario.difficulty = data[exp]["scenarios"][scn].get("difficulty")
            scenario.rules_changes = data[exp]["scenarios"][scn].get("rules-changes")
            scenario.setup_changes = data[exp]["scenarios"][scn].get("setup-changes")
            expansion.scenarios.append(scenario)
            for s in data[exp]["scenarios"][scn].get("spirit-handicaps"):
                spirit = Spirit.query.get(s)
                spirit_handicap = (
                        SpiritScenarioHandicap.query.filter_by(spirit_id=s)
                        .filter_by(scenario_id=scn)
                        .first()
                        or SpiritScenarioHandicap()
                )
                spirit_handicap.spirit = spirit
                spirit_handicap.scenario = scenario
                spirit_handicap.handicap = data[exp]["scenarios"][scn][
                    "spirit-handicaps"
                ][s]
                spirit.scenario_handicaps.append(spirit_handicap)
            for a in data[exp]["scenarios"][scn].get("adversary-handicaps"):
                adversary = Adversary.query.get(a)
                adversary_handicap = (
                        ScenarioAdversaryHandicap.query.filter_by(adversary_id=a)
                        .filter_by(scenario_id=scn)
                        .first()
                        or ScenarioAdversaryHandicap()
                )
                adversary_handicap.scenario = scenario
                adversary_handicap.adversary = adversary
                adversary_handicap.handicap = data[exp]["scenarios"][scn][
                    "adversary-handicaps"
                ][a]
                scenario.adversary_handicaps.append(adversary_handicap)
            db.session.add(scenario)


def seed_adversaries(data):
    for exp in data:
        expansion = Expansion.query.get(exp)
        for adv in data[exp].get("adversaries"):
            adversary = Adversary.query.get(adv) or Adversary()
            adversary.id = adv
            adversary.name = data[exp]["adversaries"][adv].get("name")
            adversary.additional_loss_condition = data[exp]["adversaries"][adv].get(
                "additional-loss-condition"
            )
            adversary.escalation = data[exp]["adversaries"][adv].get("escalation")
            expansion.adversaries.append(adversary)
            lvl_int = 0
            for lvl in data[exp]["adversaries"][adv].get("levels"):
                lvl_id = adv + "-" + str(lvl_int)
                adversary_level = AdversaryLevel.query.get(lvl_id) or AdversaryLevel()
                adversary_level.id = lvl_id
                adversary_level.level = lvl_int
                adversary_level.difficulty = data[exp]["adversaries"][adv]["levels"][
                    lvl_int
                ].get("difficulty")
                adversary_level.level_one_fear = data[exp]["adversaries"][adv][
                    "levels"
                ][lvl_int].get("level-one-fear")
                adversary_level.level_two_fear = data[exp]["adversaries"][adv][
                    "levels"
                ][lvl_int].get("level-two-fear")
                adversary_level.level_three_fear = data[exp]["adversaries"][adv][
                    "levels"
                ][lvl_int].get("level-three-fear")
                adversary.levels.append(adversary_level)
                db.session.add(adversary_level)
                lvl_int += 1
            for s in data[exp]["adversaries"][adv].get("spirit-handicaps"):
                spirit = Spirit.query.get(s)
                spirit_handicap = (
                        SpiritAdversaryHandicap.query.filter_by(spirit_id=s)
                        .filter_by(adversary_id=adv)
                        .first()
                        or SpiritAdversaryHandicap()
                )
                spirit_handicap.spirit = spirit
                spirit_handicap.adversary = adversary
                spirit_handicap.handicap = data[exp]["adversaries"][adv][
                    "spirit-handicaps"
                ][s]
                adversary.spirit_handicaps.append(spirit_handicap)
            db.session.add(adversary)


def seed_boards(data):
    for exp in data:
        try:
            for b in data[exp].get("boards"):
                board = Board.query.get(b) or Board()
                board.id = b
                board.expansion_id = exp
                board.is_thematic = data[exp]["boards"][b].get("thematic")
                db.session.add(board)
        except TypeError:
            pass


def seed_admin_user():
    admin_username = app.config.get("ADMIN_USERNAME")
    if not User.query.filter(User.username == admin_username).first():
        u = User()
        u.username = admin_username
        u.set_password(app.config.get("ADMIN_PASSWORD"))
        db.session.add(u)


def seed_game_data():
    data = read_game_data()
    seed_expansions(data)
    seed_spirits(data)
    seed_adversaries(data)
    seed_scenarios(data)
    seed_boards(data)
    db.session.commit()


def seed_user_data():
    seed_admin_user()
    db.session.commit()


if __name__ == "__main__":
    seed_game_data()
    seed_user_data()
