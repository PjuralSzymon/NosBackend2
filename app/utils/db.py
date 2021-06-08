from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Initialize the db and create tables
def db_init(app):
    db.init_app(app)
    # Create tables if the db doesn't exist
    with app.app_context():
        db.create_all()