from flask import Flask,render_template,redirect
from models import UserForm, Users,db

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/user")
def user():
    return render_template("user.html")

# will be update
@app.route('/user/add', methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit(): # No duplicate records
        user = Users.query.filter_by(email= form.email.data).first()
        if user is None:
            user = Users(name = form.name.data, email = form.name.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
    pass

if __name__ == '__main__':
    app.run(debug=True)

    


