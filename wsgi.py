from app.main import app
import logging
# from app.models import db


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    logging.basicConfig(level=logging.INFO)
    app.run()