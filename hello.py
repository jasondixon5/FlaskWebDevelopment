from datetime import datetime
import os

from flask import Flask, render_template, session, redirect, url_for, flash
# book import line appears to be deprecated
# from flask.ext.script import Manager
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_migrate import Migrate, MigrateCommand
from flask_moment import Moment
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

app = Flask(__name__)
# Retrieve config key or set to testing value if not set
SECRET_KEY = os.environ.get("SECRET_KEY") or "TESTING_KEY"
app.config["SECRET_KEY"] = SECRET_KEY
MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or None
app.config["MAIL_USERNAME"] = MAIL_USERNAME
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or None
app.config["MAIL_PASSWORD"] = MAIL_PASSWORD
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
# Set up DB
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = \
    "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
db = SQLAlchemy(app)

def make_shell_context():
    return dict(app=app,
                db=db,
                User=User,
                Role=Role)

manager = Manager(app)
manager.add_command("shell", 
    Shell(make_context=make_shell_context))

bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

@app.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session["known"] = False
        else:
            session["known"] = True
        session["name"] = form.name.data
        form.name.data = ""
        return redirect(url_for("index"))
    return render_template("index.html",
        form=form,
        name=session.get("name"),
        known=session.get("known", False))

@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

# Define form class
class NameForm(Form):
    name = StringField(
        "What is your name?",
        validators=[Required()])
    submit = SubmitField("Submit")

# Define DB classes
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship("User", 
        backref="role",
        lazy="dynamic")

    def __repr__(self):
        return "<Role {}>".format(self.name)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

    def __repr__(self):
        return "<User {}>".format(self.username)

if __name__ == "__main__":
    #app.run(debug=True)
    manager.run()


