from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Users(db.Model):
    name = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name
    
class Faculty(db.Model):
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    campus = db.Column(db.String(100), nullable=False)
    lecturers = relationship("Lecturer", back_populates="faculty")


class Lecturer(db.Model):
    __tablename__ = 'lecturer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    campus = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, ForeignKey('faculty.id'), nullable = False)
    faculty = relationship("Faculty", back_populates="lecturers")