from app import app
from models.artists import Artists
from models.eras import Eras
from models.tracks import Tracks
from models.sources import Source
from models.extensions import db

with app.app_context():
    Artist1 = Artists(name="Playboi Carti", user_id="lnembot14")
    db.session.add(Artist1)
    db.session.flush()

    Era1 = Eras(name="WLRV1", user_id="lnembot14", artist_id= Artist1.id)
    db.session.add(Era1)
    db.session.flush()

    Track1 = Tracks(title="Skeleton", user_id = "lnembot14", era_id = Era1.id, notes="Nice beat and mellow song")
    db.session.add(Track1)
    db.session.flush()

    Source1 = Source(track_id = Track1.id, platform = "Youtube", url="https://youtu.be/r6Vgu5ViOMY?si=_QkyGub704sygBEA", user_id="lnembot14")
    db.session.add(Source1)
    db.session.commit()

    artist_id = "1c63fc3c-03b8-45c3-896c-f038bdb57c29"
    result = db.session.get(Artists, artist_id)
    print(result)
    print(result.name if result else "No artist found")

