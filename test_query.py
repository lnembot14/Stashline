from app import app
from models.artists import Artists
from models.eras import Eras
from models.tracks import Tracks
from models.extensions import db

with app.app_context():
    Artist1 = Artists(name="Playboi Carti", user_id="lnembot14")
    db.session.add(Artist1)
    db.session.flush()

    Era1 = Eras(name="WLRV1", user_id="lnembot14", artist_id= Artist1.id)
    db.session.add(Era1)
    db.session.flush()

    Track1 = Tracks(title="Skeleton", user_id = "lnembot", era_id = Era1.id, notes="Nice beat and mellow song")
    db.session.add(Track1)
    db.session.commit()

