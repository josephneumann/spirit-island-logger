import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = (
            os.environ.get("SECRET_KEY") or "cccccclcdlfkeirjrkuthkbebfjevkvbhngcgkinvcbc"
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME") or "admin"
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or "admin"
