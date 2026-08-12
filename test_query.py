from app import app
from models.artists import Artists
from models.eras import Eras
from models.extensions import db

with app.app_context():
    Artist1 = Artists(name="Playboi Carti", user_id="lnembot14")
    db.session.add(Artist1)
    db.session.flush()

    Era1 = Eras(name="WLRV1", user_id="lnembot14", artist_id= Artist1.id)
    db.session.add(Era1)
    db.session.commit()

