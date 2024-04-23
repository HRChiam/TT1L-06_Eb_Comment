from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def keyin():
    return render_template("keyin.html")