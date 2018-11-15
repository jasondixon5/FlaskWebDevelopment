from datetime import datetime

from flask import Flask, render_template
# book import line appears to be deprecated
# from flask.ext.script import Manager
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
import os
from wtforms import StringField, SubmitField
from wtforms.validators import Required

app = Flask(__name__)
# Retrieve config key or set to testing value if not set
SECRET_KEY = os.environ.get("SECRET_KEY") or "TESTING_KEY"
app.config["SECRET_KEY"] = SECRET_KEY
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route("/", methods=["GET", "POST"])
def index():
    name = None
    form = NameForm()

    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
    
    return render_template(
        "index.html", 
        current_time=datetime.utcnow(),
        form=form,
        name=name)

@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

class NameForm(Form):
    name = StringField(
        "What is your name?",
        validators=[Required()])
    submit = SubmitField("Submit")


if __name__ == "__main__":
    #app.run(debug=True)
    manager.run()


