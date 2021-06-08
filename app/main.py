from flask import Flask,  render_template, jsonify, request, redirect, Response
from flask.helpers import send_from_directory
from werkzeug.utils import secure_filename
import os
import sys
from base64 import b64encode 
from utils.models import Photo
from utils.db import db_init, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)
#photos: List[Photo] = []

@app.route("/")
def hello():
    photos = Photo.query.order_by(Photo.id).all()
    return render_template('start.html', photos=photos)

@app.route("/upload", methods=['POST'])
def upload():
    picture = request.files['picture']
    if not picture:
        return "No picture uploaded", 400
    filename = secure_filename(picture.filename)
    mimetype = picture.mimetype
    image = Photo(img=picture.read(), mimetype=mimetype, name=filename)
    db.session.add(image)
    db.session.commit()
    return "Image uploaded successfully!", 200


@app.route("/photo/<int:id>")
def get_image(id):
    image = Photo.query.filter_by(id=id).first()
    if not image:
        return "No image with this id", 404
    base = b64encode(image.img).decode("utf-8")
    return render_template("image_show.html", name=image.name, picture=base)


@app.route("/delete/<int:id>")
def delete(id):
    image = Photo.query.filter_by(id=id).first()
    if not image:
        return "No image with this id", 404
    db.session.delete(image)
    db.session.commit()
    photos = Photo.query.order_by(Photo.id).all()
    return render_template("start.html", photos=photos)


@app.route("/edit/<int:id>")
def edit_image(id):
    image = Photo.query.filter_by(id=id).first()
    if not image:
        return "No image with this id", 404
    base = b64encode(image.img).decode("utf-8")
    return render_template("image_edit.html", name=image.name, picture=base)


def allowed_extenstion(filename):
    return '.' in filename and (filename.rsplit('.', 1)[1].lower() == 'png' or filename.rsplit('.', 1)[1].lower() == 'jpg')

def allowed_file(file_path):
    return not os.path.exists(file_path)


if __name__ == '__main__':
    app.run()