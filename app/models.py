"""
Spirit Island - Models
Copyright (c) 2020 by Joseph Neumann.  All rights reserved.
This file is part of an open-source game logger and randomizer for the tabletop game
`Spirit Island` and its expansions.  No claim is made to the rights of the `Spirit Island` content
which is owned by  `Greater Than Games`
The project is released under the MIT License Agreement.  See the LICENSE.txt file included in the package
"""
from app import db
from datetime import datetime
from typing import List
import random


class Expansion(db.Model):
    __tablename__ = "expansion"
    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    blight_cards = db.Column(db.Integer)
    spirits = db.relationship(
        "Spirit", backref="expansion", cascade="all, delete, delete-orphan"
    )
    adversaries = db.relationship(
        "Adversary", backref="expansion", cascade="all, delete, delete-orphan"
    )
    scenarios = db.relationship(
        "Scenario", backref="expansion", cascade="all, delete, delete-orphan"
    )
    boards = db.relationship(
        "Board", backref="expansion", cascade="all, delete, delete-orphan"
    )


class Spirit(db.Model):
    __tablename__ = "spirit"
    id = db.Column(db.Text, primary_key=True)  # Unique text name for character
    name = db.Column(db.Text)
    complexity = db.Column(db.Integer)  # 1/2/3 for Low/Moderate/High
    setup = db.Column(db.Text)
    offense = db.Column(db.Integer)
    control = db.Column(db.Integer)
    fear = db.Column(db.Integer)
    defense = db.Column(db.Integer)
    utility = db.Column(db.Integer)
    expansion_id = db.Column(db.Text, db.ForeignKey("expansion.id"))
    adversary_handicaps = db.relationship(
        "SpiritAdversaryHandicap",
        backref="spirit",
        cascade="all, delete, delete-orphan",
    )
    scenario_handicaps = db.relationship(
        "SpiritScenarioHandicap", backref="spirit", cascade="all, delete, delete-orphan"
    )

    def __repr__(self):
        return "<Spirit> : {}".format(self.name)

    def get_complexity(self):
        if self.complexity == 1:
            return "Low"
        elif self.complexity == 2:
            return "Moderate"
        elif self.complexity == 3:
            return "High"
        return "Unknown"

    def get_game_wins(self) -> int:
        """Get count of games this spirit has won"""
        return (
            Game.query.filter(Game.spirits.any(id=self.id))
            .filter(Game.is_complete)
            .filter(Game.is_victory)
            .count()
        )

    def get_game_losses(self):
        """Get count of games this spirit has lost"""
        return (
            Game.query.filter(Game.spirits.any(id=self.id))
            .filter(Game.is_complete)
            .filter(~Game.is_victory)
            .count()
        )


class Adversary(db.Model):
    __tablename__ = "adversary"
    id = db.Column(db.Text, primary_key=True)  # Unique text name for character
    name = db.Column(db.Text)
    additional_loss_condition = db.Column(db.Text)
    escalation = db.Column(db.Text)
    expansion_id = db.Column(db.Text, db.ForeignKey("expansion.id"))
    levels = db.relationship(
        "AdversaryLevel",
        backref="adversary",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
    )
    spirit_handicaps = db.relationship("SpiritAdversaryHandicap", backref="adversary")
    scenario_handicaps = db.relationship(
        "ScenarioAdversaryHandicap", backref="adversary"
    )


class AdversaryLevel(db.Model):
    __tablename__ = "adversary_level"
    id = db.Column(db.Text, primary_key=True)
    adversary_id = db.Column(db.Text, db.ForeignKey("adversary.id"))
    level = db.Column(db.Integer)
    difficulty = db.Column(db.Integer)
    level_one_fear = db.Column(db.Integer)
    level_two_fear = db.Column(db.Integer)
    level_three_fear = db.Column(db.Integer)
    games = db.relationship("Game", backref="adversary_level")


class Scenario(db.Model):
    __tablename__ = "scenario"
    id = db.Column(db.Text, primary_key=True)  # Unique text name for character
    name = db.Column(db.Text)
    difficulty = db.Column(db.Integer)
    expansion_id = db.Column(db.Text, db.ForeignKey("expansion.id"))
    spirit_handicaps = db.relationship(
        "SpiritScenarioHandicap",
        backref="scenario",
        cascade="all, delete, delete-orphan",
    )
    adversary_handicaps = db.relationship(
        "ScenarioAdversaryHandicap",
        backref="scenario",
        cascade="all, delete, delete-orphan",
    )
    games = db.relationship("Game", backref="scenario")


class SpiritAdversaryHandicap(db.Model):
    __tablename__ = "spirit_adversary_handicap"
    spirit_id = db.Column(db.Text, db.ForeignKey("spirit.id"), primary_key=True)
    adversary_id = db.Column(db.Text, db.ForeignKey("adversary.id"), primary_key=True)
    handicap = db.Column(db.Integer, nullable=False)


class SpiritScenarioHandicap(db.Model):
    __tablename__ = "spirit_scenario_handicap"
    spirit_id = db.Column(db.Text, db.ForeignKey("spirit.id"), primary_key=True)
    scenario_id = db.Column(db.Text, db.ForeignKey("scenario.id"), primary_key=True)
    handicap = db.Column(db.Integer, nullable=False)


class ScenarioAdversaryHandicap(db.Model):
    __tablename__ = "scenario_adversary_handicap"
    scenario_id = db.Column(db.Text, db.ForeignKey("scenario.id"), primary_key=True)
    adversary_id = db.Column(db.Text, db.ForeignKey("adversary.id"), primary_key=True)
    handicap = db.Column(db.Integer, nullable=False)


game_board = db.Table(
    "game_board",
    db.Model.metadata,
    db.Column("game_id", db.Integer, db.ForeignKey("game.id")),
    db.Column("board_id", db.Text, db.ForeignKey("board.id")),
)


class Board(db.Model):
    __tablename__ = "board"
    id = db.Column(db.Text, primary_key=True)
    is_thematic = db.Column(db.Boolean, default=False, nullable=False)
    expansion_id = db.Column(db.Text, db.ForeignKey("expansion.id"))


spirit_game_play = db.Table(
    "spirit_game_play",
    db.Model.metadata,
    db.Column("game_id", db.Integer, db.ForeignKey("game.id")),
    db.Column("spirit_id", db.Text, db.ForeignKey("spirit.id")),
)

game_expansion = db.Table(
    "game_expansion",
    db.Model.metadata,
    db.Column("game_id", db.Integer, db.ForeignKey("game.id")),
    db.Column("expansion_id", db.Text, db.ForeignKey("expansion.id")),
)


class Game(db.Model):
    """
    Database Model / Object to represent a single game of Spirit-Island
    """

    # Database Columns and Relationships
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, default=datetime.today())
    player_count = db.Column(db.Integer)
    spirits = db.relationship("Spirit", secondary=spirit_game_play, backref="games")
    boards = db.relationship("Board", secondary=game_board, backref="games")
    expansions = db.relationship("Expansion", secondary=game_expansion, backref="games")
    adversary_level_id = db.Column(db.Text, db.ForeignKey("adversary_level.id"))
    scenario_id = db.Column(db.Text, db.ForeignKey("scenario.id"))
    difficulty = db.Column(db.Integer)
    handicap = db.Column(db.Integer)
    score = db.Column(db.Integer)
    is_complete = db.Column(db.Boolean, default=False, nullable=False)
    is_victory = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Integer)
    notes = db.Column(db.Text)

    def __init__(
        self,
        player_count: int,
        date: datetime = datetime.today(),
        expansions: List[str] = None,
    ):
        """
        Custom initialization
        You must supply some basic information to create a Game including number of players
        and the expansions to be used.

        :param player_count: Int, count of players playing the game
        :param date: Date of the game being played, default today
        :param expansions: List of IDs of expansions to use beyond base game
            ex: ["branch-and-claw","jagged-earth"]
        """
        if not (
            isinstance(player_count, int) and player_count > 0 and player_count <= 4
        ):
            raise ValueError("Player count must be integer value of 1-4 players")
        self.player_count = player_count  # Player count is required to initialize Game
        self.date = date
        self.difficulty = 0
        self.handicap = 0
        self.expansions = [Expansion.query.get("base")]

        # Handle expansions
        if expansions:
            for e in expansions:
                self.expansions.append(Expansion.query.get(e))

    def get_all_expansion_spirits(self) -> List[Spirit]:
        """
        Retrieve a scalar of all Spirits that are available given the game Expansions
        :return A list of matching Spirit objects
        """
        return Spirit.query.filter(
            Spirit.expansion_id.in_([e.id for e in self.expansions])
        ).all()

    def get_available_spirits(self, max_complexity: int) -> List[Spirit]:
        """
        Retrieve a scalar of all Spirits that are available given the game Expansions
        Excludes any spirits already assigned to the game (since they are no longer available)

        :param max_complexity: Int (1-3) Maximum complexity of spirit to retrieve.
            1: Low complexity
            2: Moderate complexity
            3: High complexity

        :return A list of matching Spirit objects
        """
        return (
            Spirit.query.filter(
                Spirit.expansion_id.in_([e.id for e in self.expansions])
            )
            .filter(Spirit.complexity <= max_complexity)
            .filter(~Spirit.id.in_([s.id for s in self.spirits]))
            .all()
        )

    def assign_random_spirits(self, max_complexity: int) -> None:
        """
        Assign random spirits to the game
        Will retain any spirits already assigned to the game manually
        If all spirits are already assigned, do nothing

        :param max_complexity: int - Maximum complexity of spirit to assign
            1: Low complexity
            2: Moderate complexity
            3: High complexity

        :return None

        """
        open_spirit_slots = self.player_count - len(self.spirits)
        self.spirits.extend(
            random.sample(self.get_available_spirits(max_complexity), open_spirit_slots)
        )

    def get_available_scenarios(self, max_difficulty: int) -> List[Scenario]:
        """
        Retrieve a scalar of all Scenarios that are available given the games Expansions
        Do not exceed the maximum specified difficulty

        :param max_difficulty: Int, 0-10, Maximum difficulty of scenarios to retrieve
        :return List of matching Scenario objects
        """
        return (
            Scenario.query.filter(
                Scenario.expansion_id.in_([e.id for e in self.expansions])
            )
            .filter(Scenario.difficulty <= max_difficulty)
            .all()
        )

    def assign_random_scenario(self, max_difficulty: int) -> None:
        """
        Randomly assign a Scenario to the Game if one is not already selected
        :param max_difficulty: Int, 0-10, Maximum difficulty of scenarios to retrieve
        :return:
        """
        if not self.scenario:
            self.scenario = random.choice(self.get_available_scenarios(max_difficulty))

    def get_available_adversary_levels(
        self, max_difficulty: int
    ) -> List[AdversaryLevel]:
        """
        Retrieve a scalar of all Adversaries that are available given the games Expansions
        :param max_difficulty: Int (0-10) Maximum difficulty of AdversaryLevel to assign
        :return List of AdversaryLevel objects
        """
        return (
            AdversaryLevel.query.join(Adversary)
            .filter(Adversary.expansion_id.in_([e.id for e in self.expansions]))
            .filter(AdversaryLevel.difficulty <= max_difficulty)
            .all()
        )

    def assign_random_adversary(self, max_difficulty: int) -> None:
        """
        Randomly assign an Adversary (at a specific level) to the Game
        If Adversary is already selected, do nothing

        :param max_difficulty: Int (0-10) Maximum difficulty of AdversaryLevel to assign
        :return: None
        """
        if not self.adversary_level:
            self.adversary_level = random.choice(
                self.get_available_adversary_levels(max_difficulty)
            )

    def get_available_boards(self, thematic: bool) -> List[Board]:
        """
        Retrieve a scalar of all Boards that are available given the games Expansions
        Do not return Boards already assigned to the game (they are already used)
        Do allow for using thematic or non thematic boards by preference

        :param thematic: Whether to use thematic boards
        :return List of Board objects
        """
        return (
            Board.query.filter(Board.expansion_id.in_([e.id for e in self.expansions]))
            .filter(~Board.id.in_(b.id for b in self.boards))
            .filter(Board.is_thematic.is_(thematic))
            .all()
        )

    def assign_random_boards(self, thematic: bool) -> None:
        """
        Assign a random set of boards to the game
        If all boards are already assigned, do nothing

        :param thematic: Bool - Whether to use thematic boards
        :return: None
        """
        open_board_slots = self.player_count - len(self.boards)
        self.boards.extend(
            random.sample(
                self.get_available_boards(thematic=thematic), open_board_slots
            )
        )

    @property
    def is_thematic(self) -> bool:
        """
        Helper property to determine whether game is using thematic boards
        :return: Bool - True if game is using thematic boards, False if not.
        """
        if not self.boards:
            raise AttributeError("No boards selected for Game")
        for b in self.boards:
            if b.is_thematic:
                return True
        return False

    def calculate_difficulty(self) -> int:
        """
        Calculate the game difficulty
            Base difficulty is 0
            Thematic boards add 3 difficulty, unless using branch and claw, then only 1
            A scenario may add to game difficulty
            An Adversary may add to game difficulty

        :return: Integer value of game difficulty
        """
        # Calculate difficulty as sum of Scenario and Adversary
        self.difficulty = 0
        if self.boards:
            # Special rules for branch-and-claw expansion
            if self.is_thematic:
                bac = Expansion.query.get("branch-and-claw")
                if bac in self.expansions:
                    self.difficulty += 1
                else:
                    self.difficulty += 3
        # Add adversary difficulty
        if self.adversary_level:
            self.difficulty += self.adversary_level.difficulty
        # Add scenario difficulty
        if self.scenario:
            self.difficulty += self.scenario.difficulty
        return self.difficulty

    def calculate_handicap(self):
        """Calculate net handicap from spirit/adversary/scenario interactions"""
        self.handicap = 0
        for s in self.spirits:
            if self.adversary_level:
                sah = (
                    SpiritAdversaryHandicap.query.filter_by(spirit_id=s.id)
                    .filter_by(adversary_id=self.adversary_level.adversary_id)
                    .first()
                )
                if sah:
                    self.handicap += sah.handicap
            if self.scenario:
                ssh = (
                    SpiritScenarioHandicap.query.filter_by(spirit_id=s.id)
                    .filter_by(scenario_id=self.scenario.id)
                    .first()
                )
                if ssh:
                    self.handicap += ssh.handicap
        if self.scenario and self.adversary_level:
            scn_adv_handicap = (
                ScenarioAdversaryHandicap.query.filter_by(scenario_id=self.scenario.id)
                .filter_by(adversary_id=self.adversary_level.adversary_id)
                .first()
            )
            if scn_adv_handicap:
                self.handicap += scn_adv_handicap.handicap

    def reset_game(self) -> None:
        """
        Helper method to clear some common configuration of the game which may
        be randomized
        Will nullify spirits, boards, scenarios and adversary.
        :return: None
        """
        self.spirits = []
        self.scenario = None  # Note this comes from backref on Scenario
        self.adversary_level = None  # Note this comes from backref on adversary_level
        self.difficulty = None
        self.boards = []

    def randomize(
        self,
        use_thematic_boards: bool = True,
        spirit_max_complexity: int = 3,
        scenario_max_difficulty: int = None,
        adversary_max_difficulty: int = None,
        force: bool = False,
    ):
        """
        Randomize a Game of Spirit Island
        Will randomize:
            1) Spirit selection
            2) Board selection
            3) Scenario selection (if desired) at or under the indicated difficulty
            4) Adversary selection (if desired) at or under the indicated difficulty

        :param use_thematic_boards: Bool - Whether to use Thematic boards for game
        :param spirit_max_complexity: Bool - Maximum complexity of spirits to randomly
            assign.  1: Low, 2: Moderate, 3: High
        :param scenario_max_difficulty: Int (0-10) - Max difficulty of Scenario to
            randomly select.  If None, no scenario will be selected.
        :param adversary_max_difficulty: Int (1-10) - Max difficulty of Adversary to
            randomly select. If None, no adversary will be selected.
        :param force: Bool - Whether to force over-write pre-selected game data
        :return: None

        !Important! - When using randomize, if you wish to pre-configure some of these
        game attributes, do so before calling randomize.  For example, set a spirit
        of your choosing, or an adversary etc.  They will not be overwritten, unless
        the force option is used.
        """
        # Reset game attributes if forcing randomization
        if force:
            self.reset_game()
        # Randomly fill remaining spirits slots
        self.assign_random_spirits(spirit_max_complexity)
        # Randomly fill remaining board slots
        self.assign_random_boards(use_thematic_boards)
        # Randomly assign scenario
        if scenario_max_difficulty:
            self.assign_random_scenario(scenario_max_difficulty)
        # Randomly assign an adversary
        if adversary_max_difficulty:
            self.assign_random_adversary(adversary_max_difficulty)
        # Now calculate the difficulty and net handicap of the game as configured
        self.calculate_difficulty()
        self.calculate_handicap()

    def calculate_score(
        self, victory: bool, invader_cards_in_deck: int, dahan: int, blight: int
    ) -> int:
        """
        Assign a score to the game
        If you would like to score your games (to compare your group's performance across game plays):
            Victory: Score 5x Difficulty,
                    +10 bonus for winning,
                    +2 per Invader Card remaining in the deck.
            Defeat: Score 2x Difficulty,
                    +1 per Invader Card not in the deck (both in the discard and face-up under Invader Actions).
            Victory or Defeat: +1 per X living Dahan and -1 per X Blight on the island,
                where X is the number of players in the game.

        :param victory: Bool - Did you win the game?
        :param invader_cards_in_deck:  Int - Cards left in invader deck (face down)
        :param dahan: Int - Dahan left on board
        :param blight: Int - Blight on the board
        :return: Int Score
        """
        self.score = 0
        self.is_complete = True
        self.is_victory = victory
        if self.is_victory:
            self.score = 5 * self.difficulty
            self.score += 10
            self.score += 2 * invader_cards_in_deck
        else:
            self.score = 2 * self.difficulty
            self.score += 12 - invader_cards_in_deck
        self.score += dahan // self.player_count
        self.score -= blight // self.player_count
        return self.score

    @property
    def status(self):
        if not self.is_complete:
            return "Incomplete"
        return "Victory" if self.is_victory else "Defeat"
