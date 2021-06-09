from .db import db

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    render_data = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
