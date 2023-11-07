from flask import Flask, redirect, url_for, render_template, request, session, g, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = "NothingMuch"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///user-data-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = "OFF"
db = SQLAlchemy(app)



@app.route("/")
def home():
    return render_template('home.html')



@app.route("/lifestyle")
def lifestyle_home():
    return "haha"

@app.route("/healthcare")
def healthcare_home():
    return "haha"

@app.route("/healthcare/admin")
def healthcare_admin():
    return "haha"

@app.route("/healthcare/login")
def healthcare_login():
    return ""

@app.route("/healthcare/register")
def healthcare_register():
    return ""

@app.route("/healthcare/create_profile")
def create_profile():
    return ""

@app.route("/healthcare/view")
def healthcare_view():
    return ""

@app.route("/healthcare/input_data")
def healthcare_input_data():
    return ""

if __name__ == "__main__":
    app.run(debug=True)

