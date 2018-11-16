from datetime import datetime

from flask import Flask, render_template, session, redirect, url_for, flash
# book import line appears to be deprecated
# from flask.ext.script import Manager
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from flask_sqlalchemy import SQLAlchemy
import os
from wtforms import StringField, SubmitField
from wtforms.validators import Required

app = Flask(__name__)
# Retrieve config key or set to testing value if not set
SECRET_KEY = os.environ.get("SECRET_KEY") or "TESTING_KEY"
app.config["SECRET_KEY"] = SECRET_KEY
# Set up DB
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = \
    "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
db = SQLAlchemy(app)

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route("/", methods=["GET", "POST"])
def index():
    
    form = NameForm()

    if form.validate_on_submit():
        old_name = session.get("name")
        if old_name is not None and old_name != form.name.data:
            flash("Looks like you have changed your name!")
        session["name"] = form.name.data
        return redirect(url_for("index"))
    
    return render_template(
        "index.html", 
        current_time=datetime.utcnow(),
        form=form,
        name=session.get("name"))

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


