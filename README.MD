# ![dahan] Spirit Island Logger  ![dahan]
An open-source game-logger and randomizer utility for the tabletop game [*Spirit Island*](https://store.greaterthangames.com/spirit-island.html) from Greater Than Games.

# Feature Overview

## Data
Python data model describing *Spirit Island* gameplay, implemented with the SQLAlchemy ORM.  By default game configuration data and gameplay results will be persisted in a [SQLite](https://www.sqlite.org/index.html), unless an alternative db connection is defined.
![erd]


## Utilities
Utilities to randomly configure new games based on user-defined preferences such as: expansions to use, spirit complexity, adversary and scenario difficulty etc.
Utilities to calculate the score of completed *Spirit Island* games.


## Web App
A [Flask](https://flask.palletsprojects.com/en/1.1.x/) web-app for interacting with the data. You can use this tool to
track gameplay, randomize games and score them.

### Game History / Home Page
![index]


### Game Editor
![edit_game]


### Game Randomizer
![randomize_game]

### Game Scorer
![score_game]


## Installation and Configuration
Clone this repository to your machine
```bash
git clone https://github.com/{thisrepo}
```
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install package dependencies.

```bash
pip install -r requirements.txt
```

Edit or adjust configuration for the project.  
You may wish to customize the database connection details in `config.py` to change the location of the SQLite database or to [configure an alternative database connection.](https://docs.sqlalchemy.org/en/13/core/engines.html)

Set the `FLASK_APP` environment variable on your machine
```bash
export FLASK_APP=spirit_island.py
```

Run the Alembic database migrations to head. This will create the database, it's relations and will also seed the tables with the data from `game_data.json`
```bash
flask db upgrade
```

## Usage
Run the Flask web app.  You can use the development server that `Flask` has built-in, or choose a more robust way to run and serve the app.
```
flask run
```
You might see something like
```bash
 * Serving Flask app "spirit_island.py:app" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Open the index page at the appropriate URL and you're all set!

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/) License.  See `LICENSE.txt`

[dahan]: assets/dahan.png
[index]: assets/screenshots/index.png
[edit_game]: assets/screenshots/edit_game.png
[randomize_game]: assets/screenshots/randomize_game.png
[score_game]: assets/screenshots/score_game.png
[erd]:assets/screenshots/data_erd.png