from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
from flask import Flask, render_template, redirect,url_for
from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired

# Create Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/user")
def user():
    return render_template("user.html")

@app.route("/comment")
def comment():
    return render_template("comment.html")

# Configure MySQL DB URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://KEEHUIYEE:KeE-0924@localhost/users'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Create Model
class Users(db.Model):
    name = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(20),nullable = False)

    def __repr__(self):
        return '<Name %r>' % self.name
# Create User Form
class UserForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")



@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit(): 
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        our_users = Users.query.all()  # Assuming data_added is not defined in your model
    return render_template("login.html", form=form, name=name, our_users=our_users)

if __name__ == '__main__':
    app.run(debug=True)
