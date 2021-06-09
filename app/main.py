from flask import Flask, url_for, render_template, request, redirect, send_file
from flask.helpers import send_from_directory
from werkzeug.utils import secure_filename
from base64 import b64encode, b64decode
import os
import sys
import io
import cv2
import numpy as np
#from utils.models import Photo
#from utils.db import db_init, db
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# Initialize the db and create tables
def db_init(app):
    db.init_app(app)
    # Create tables if the db doesn't exist
    with app.app_context():
        db.create_all()

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    render_data = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)

#### Flask app ####

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)


@app.route("/")
def hello():
    photos = Photo.query.order_by(Photo.id).all()
    return render_template('start.html', photos=photos)

@app.route("/upload", methods=['POST'])
def upload():
    picture = request.files['picture']
    if not picture:
        return "No picture uploaded" + '''<br><br><a href="/">Back</a>''', 400
    filename = secure_filename(picture.filename)
    data = picture.read()
    render_pic = b64encode(data).decode('ascii') 
    mimetype = picture.mimetype
    image = Photo(name=filename, data=data, render_data=render_pic, mimetype=mimetype)
    db.session.add(image)
    db.session.commit()
    return "Image uploaded successfully!" + '''<br><br><a href="/">Back</a>''', 200


@app.route("/photo/<int:id>")
def get_image(id):
    image = Photo.query.filter_by(id=id).first()
    if not image:
        return "No image with this id", 404
    urlback = ""
    return render_template("image_show.html", image=image, base=image.render_data, urlback=urlback)

@app.route("/delete/<int:id>")
def delete(id):
    image = Photo.query.filter_by(id=id).first()
    if not image:
        return "No image with this id", 404
    db.session.delete(image)
    db.session.commit()
    #photos = Photo.query.order_by(Photo.id).all()
    return redirect(url_for("hello"))

@app.route("/edit/<int:id>")
def edit_image(id):
    image = Photo.query.filter_by(id=id).first()
    if not image:
        return "No image with this id", 404
    #base = b64encode(image.img).decode("utf-8")
    return render_template("image_edit.html", image=image)

#### Editing Images ####

@app.route("/edit/<int:id>/resize", methods=['POST'])
def resize_image(id):
    picture = Photo.query.filter_by(id=id).first()
    if not picture:
        return "No image with this id", 404
    img = convert_to_cv2(picture)
    width = request.form['width']
    height = request.form['height']
    if not width:
        width = img.shape[1]
    if not height:
        height = img.shape[0]
    dim = (int(width), int(height))
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    final = convert_to_base64(resized)
    urlback = "edit/" + str(picture.id)
    return render_template("image_show.html", image=picture, base=final, urlback=urlback)

@app.route("/edit/<int:id>/crop", methods=['POST'])
def crop_image(id):
    picture = Photo.query.filter_by(id=id).first()
    if not picture:
        return "No image with this id", 404
    img = convert_to_cv2(picture)
    left = request.form['left']; right = request.form['right']
    top = request.form['top']; bottom = request.form['bottom']
    if not left:
        left = 0
    if not right:
        right = 0
    if not top:
        top = 0
    if not bottom:
        bottom = 0
    startY = 0 + int(top); endY = img.shape[0] - int(bottom)
    startX = 0 + int(left); endX = img.shape[1] - int(right)
    cropped = img[startY:endY, startX:endX]
    final = convert_to_base64(cropped)
    urlback = "edit/" + str(picture.id)
    return render_template("image_show.html", image=picture, base=final, urlback=urlback)

@app.route("/edit/<int:id>/inverse", methods=['POST'])
def inverse_image(id):
    picture = Photo.query.filter_by(id=id).first()
    if not picture:
        return "No image with this id", 404
    img = convert_to_cv2(picture)
    inv = cv2.bitwise_not(img)
    final = convert_to_base64(inv)
    urlback = "edit/" + str(picture.id)
    return render_template("image_show.html", image=picture, base=final, urlback=urlback)

@app.route("/edit/<int:id>/blur", methods=['POST'])
def blur_image(id):
    picture = Photo.query.filter_by(id=id).first()
    if not picture:
        return "No image with this id", 404
    img = convert_to_cv2(picture)
    blur = cv2.blur(img, (5,5))
    final = convert_to_base64(blur)
    urlback = "edit/" + str(picture.id)
    return render_template("image_show.html", image=picture, base=final, urlback=urlback)

@app.route("/edit/<int:id>/sobel", methods=['POST'])
def sobel_image(id):
    picture = Photo.query.filter_by(id=id).first()
    if not picture:
        return "No image with this id", 404
    img = convert_to_cv2(picture)
    img = cv2.GaussianBlur(img,(3,3),0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    grad_x = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
    grad_y = cv2.Sobel(gray, cv2.CV_16S, 0, 1, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
    final = convert_to_base64(grad)
    urlback = "edit/" + str(picture.id)
    return render_template("image_show.html", image=picture, base=final, urlback=urlback)


### Additional methods ###
def allowed_extenstion(filename):
    return '.' in filename and (filename.rsplit('.', 1)[1].lower() == 'png' or filename.rsplit('.', 1)[1].lower() == 'jpg')

def allowed_file(file_path):
    return not os.path.exists(file_path)

def convert_to_cv2(picture):
    im_b64 = b64encode(picture.data)
    im_bytes = b64decode(im_b64)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8) 
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
    return img

def convert_to_base64(image):
    _, im_arr = cv2.imencode('.jpg', image)  # im_arr: image in Numpy one-dim array format.
    im_bytes = im_arr.tobytes()
    im_b64 = b64encode(im_bytes).decode('utf-8')
    return im_b64


if __name__ == '__main__':
    app.run(debug=True)