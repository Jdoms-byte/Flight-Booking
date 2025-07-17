# drop_table.py
from web import db, create_app
from web.models import Aircraft

app = create_app()

with app.app_context():
    Aircraft.__table__.drop(db.engine)
    print("Flight table dropped.")
