from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
from app import app
from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired

#mySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://KEEHUIYEE:KeE-0924@localhost/users'

# Initialize The Database
db = SQLAlchemy

# Create Model
class Users(db.Model):
    name = db.Column(db.String(20), primary_key = True)
    email = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(20), nullable = False)

# Create User Form
class UserForm(FlaskForm):
    name = StringField("username", validators=[DataRequired()])
    email =  StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")



