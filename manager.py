from datetime import timedelta

from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session

app = Flask(__name__)

class Config(object):
    DEBUG = True
    SECRET_KEY = "fsfssfs"

    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    SESSION_TYPE = "redis"
    SESSION_REDIS = StrictRedis(host = REDIS_HOST,port= REDIS_PORT)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=5)#设置session有效期

app.config.from_object(Config)

db = SQLAlchemy(app)

redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

Session(app)

@app.route('/')
def hello_world():
    redis_store.set("name","laowang")
    print(redis_store.get("name"))

    session["name"] = "zhangsan"
    print(session.get("name"))
    return "helloworld"

if __name__ == '__main__':

    app.run()