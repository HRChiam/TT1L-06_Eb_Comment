from flask import Flask, Blueprint, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)

@app.route("/")
def admin():
    return render_template("index.html")

if __name__ == "__main__":
    # Run the application
    app.run(debug=True, port=5000)
