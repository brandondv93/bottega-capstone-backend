from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(144), unique=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        fields = ('username', 'password')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route('/user', methods=['POST'])
def add_user():
    username = request.json['username']
    password = request.json['password']

    new_user = User(username, password)

    db.session.add(new_user)
    db.session.commit()

    user = User.query.get(new_user.id)

    return user_schema.jsonify(user)


@app.route('/login', methods=['POST'])
def login():
    username = request.json['email']
    password = request.json['password']

    user = User.query.filter_by(username=username).first()

    if user:
        if username == user.username and password == user.password:
            hashed_password = bcrypt.generate_password_hash(
                user.username).decode('utf-8')
            return {
                "status": "LOGGED_IN",
                "token": hashed_password
            }
        else:
            return {
                "status": "NOT_LOGGED_IN",
                "message": "Incorrect password"
            }
    else:
        return {
            "status": "NOT_LOGGED_IN",
            "message": "Incorrect username"
        }


@app.route("/users", methods=["GET"])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)


@app.route("/user/<id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)


@app.route("/user/<id>", methods=["DELETE"])
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)


class Notecard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    correct_answer = db.Column(db.String(100), unique=False)
    incorrect_answer1 = db.Column(db.String(100), unique=False)
    incorrect_answer2 = db.Column(db.String(100), unique=False)
    incorrect_answer3 = db.Column(db.String(100), unique=False)
    question = db.Column(db.String(144), unique=False)

    def __init__(self, correct_answer, incorrect_answer1, incorrect_answer2, incorrect_answer3, question):
        self.correct_answer = correct_answer
        self.incorrect_answer1 = incorrect_answer1
        self.incorrect_answer2 = incorrect_answer2
        self.incorrect_answer3 = incorrect_answer3
        self.question = question


class NotecardSchema(ma.Schema):
    class Meta:
        fields = ('correct_answer', 'incorrect_answer1',
                  'incorrect_answer2', 'incorrect_answer3', 'question')


notecard_schema = NotecardSchema()
notecards_schema = NotecardSchema(many=True)


@app.route('/notecard', methods=['POST'])
def add_notecard():
    correct_answer = request.json['correct_answer']
    incorrect_answer1 = request.json['incorrect_answer1']
    incorrect_answer2 = request.json['incorrect_answer2']
    incorrect_answer3 = request.json['incorrect_answer3']
    question = request.json['question']

    new_notecard = Notecard(correct_answer, incorrect_answer1,
                            incorrect_answer2, incorrect_answer3, question)

    db.session.add(new_notecard)
    db.session.commit()

    notecard = Notecard.query.get(new_notecard.id)

    return notecard_schema.jsonify(notecard)


@app.route("/notecards", methods=["GET"])
def get_notecards():
    all_notecards = Notecard.query.all()
    result = notecards_schema.dump(all_notecards)
    return result


@app.route("/notecard/<id>", methods=["GET"])
def get_notecard(id):
    notecard = Notecard.query.get(id)
    return notecard_schema.jsonify(notecard)


@app.route("/notecard/<id>", methods=["DELETE"])
def notecard_delete(id):
    notecard = Notecard.query.get(id)
    db.session.delete(notecard)
    db.session.commit()

    return notecard_schema.jsonify(notecard)


if __name__ == '__main__':
    app.run(debug=True)
