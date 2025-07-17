# manage_db.py
import sys
from web import db, create_app
from web.models import SeatClass  # Add other models if needed

app = create_app()

with app.app_context():
    if len(sys.argv) > 1:
        if sys.argv[1] == "create":
            db.create_all()
            print("✅ All database tables created.")
        elif sys.argv[1] == "drop":
            SeatClass.__table__.drop(db.engine)
            print("🗑️ Aircraft table dropped.")
        else:
            print("⚠️ Invalid command. Use: python manage_db.py [create|drop]")
    else:
        print("ℹ️ Please provide a command: python manage_db.py [create|drop]")
