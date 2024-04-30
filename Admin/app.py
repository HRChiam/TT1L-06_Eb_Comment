from flask import Flask,render_template,redirect

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/user")
def user():
    return render_template("user.html")

if __name__ == '__main__':
    app.run(debug=True)

    


