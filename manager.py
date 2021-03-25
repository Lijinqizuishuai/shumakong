from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

class Config(object):
    DEBUG=True

    SQLAlCHEMY_DATABASE_URL="mysql+pymysql://root:123456@localhost:3306/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS =False


db = SQLAlchemy(app)

@app.route('/')
def hello_world():
    return "helloworld"

if __name__=='__main__':
    app.run()