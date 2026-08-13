from flask import Blueprint, jsonify, request
import sqlalchemy
from models.tracks import Tracks
from models.extensions import db

track_route = Blueprint("track_route", __name__)

@track_route.route('/track', methods=['GET', 'POST'])
def track():
    if request.method == "GET":
        track_info = db.session.scalars(db.select(Tracks)).all()
        track_list = [{"id":track.id, "era_id": track.era_id, "title": track.title, "notes": track.notes, "user_id" : track.user_id, "created_at": track.created_at} for track in track_info]
        return jsonify(track_list), 200
    elif request.method == "POST":
        added_track = request.json
        if added_track.get("user_id") is None or added_track.get("title") is None or added_track.get("era_id") is None:
            return "Missing required field(s)", 400
        else:
            song = Tracks(title= added_track["title"], user_id = added_track["user_id"],era_id = added_track["era_id"])
            db.session.add(song)
            try:
                db.session.commit()
                track_data = {"id": song.id, "era_id": song.era_id, "title": song.title, "notes": song.notes, "user_id": song.user_id, "created_at": song.created_at}
                return jsonify(track_data), 400
            except sqlalchemy.exc.IntegrityError:
                db.session.rollback()
                return "Invalid Artist_Id, please try again", 400
