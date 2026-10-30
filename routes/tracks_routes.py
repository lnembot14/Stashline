from flask import Blueprint, current_app, jsonify, request
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
                return jsonify(track_data), 200
            except sqlalchemy.exc.IntegrityError:
                db.session.rollback()
                return "Invalid Artist_Id, please try again", 400

@track_route.route('/tracks/<uuid:track_id>', methods = ['PATCH', 'DELETE'])
def track_detail(track_id):
    if request.method == "DELETE":
        try:
            selected_track = db.session.get(Tracks, track_id)
            if selected_track is None:
                return "Track not found", 404
            db.session.delete(selected_track)
            db.session.commit()
            return "Item deleted", 200
        except (sqlalchemy.exc.DataError, sqlalchemy.exc.IntegrityError):
            db.session.rollback()
            return "Invalid track data", 400
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to delete track")
            return "Unable to delete track", 500
    elif request.method == "PATCH":
        if not request.is_json:
            return "Request must contain JSON", 415
        updates = request.get_json()
        if not isinstance(updates, dict):
            return "JSON body must be an object", 400
        if "title" in updates:
            if not isinstance(updates["title"], str) or not updates["title"].strip():
                return "Title must be a non-empty string", 400

        try:
            track_info = db.session.get(Tracks, track_id)
            if track_info is None:
                return "Track not found", 404

            if "title" in updates:
                track_info.title = updates["title"].strip()

            db.session.commit()
            return jsonify({
                "id": track_info.id,
                "era_id": track_info.era_id,
                "title": track_info.title,
                "notes": track_info.notes,
                "user_id": track_info.user_id,
                "created_at": track_info.created_at
            }), 200
        except (sqlalchemy.exc.DataError, sqlalchemy.exc.IntegrityError):
            db.session.rollback()
            return "Invalid track data", 400
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to update track")
            return "Unable to update track", 500
