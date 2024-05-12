from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    campus = db.Column(db.String(100), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Lecturer %r>' % self.name
