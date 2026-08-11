from app import app
from models.artists import Artists
from models.extensions import db

db.init_app(app)

with app.app_context():
    Artist1 = Artists(name="Playboi Carti", user_id="lnembot14")

    db.session.add(Artist1)

    db.session.commit()
