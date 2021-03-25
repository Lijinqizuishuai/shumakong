from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from config import config_dict
from flask import Flask
from  info.modules.index import index_blue
def create_app(config_name):
    app = Flask(__name__)

    config = config_dict.get(config_name)


    app.config.from_object(config)

    db = SQLAlchemy(app)

    redis_store = StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

    Session(app)

    CSRFProtect(app)

    app.register_blueprint(index_blue)

    return app