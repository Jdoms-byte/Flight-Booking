# create_db.py
from web import db, create_app
from web.models import Aircraft,SeatClass
app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created.")
