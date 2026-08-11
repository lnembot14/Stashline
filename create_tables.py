from app import app
from models.extensions import db
from models.artists import Artists
from models.eras import Eras
from models.sources import Source
from models.tracks import Tracks

db.init_app(app)

with app.app_context():
    db.create_all()