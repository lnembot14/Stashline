from flask import Blueprint, current_app, request, jsonify
import sqlalchemy
from models.saved_tracks import SavedTracks
from models.extensions import db
from routes.validation import read_json, record_dict


saved_track_route = Blueprint("saved_track_route", __name__)

# Saved entries have no editable metadata yet.
EDITABLE_FIELDS = {}
# Temporary until user_id comes from verified authentication.
CREATE_FIELDS = {'user_id': 'uuid', 'track_id': 'uuid'}
RESPONSE_FIELDS = ('id', 'user_id', 'track_id', 'saved_at')


@saved_track_route.route('/saved_tracks', methods=['GET', 'POST'])
def saved_tracks():
    if request.method == 'GET':
        # TODO: List the authenticated user's saved tracks.
        try:
            saved_tracks = db.session.scalars(db.select(SavedTracks)).all()
            return jsonify([record_dict(track, RESPONSE_FIELDS) for track in saved_tracks]), 200
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to list saved tracks")
            return "Unable to retrieve saved tracks", 500

    if request.method == 'POST':
        # TODO: Save a track for the authenticated user.
        columns = read_json(CREATE_FIELDS, required=('user_id', 'track_id'))
        try:
            saved = SavedTracks(**columns)
            db.session.add(saved)
            db.session.commit()
            return jsonify(record_dict(saved, RESPONSE_FIELDS)), 201
        except sqlalchemy.exc.IntegrityError as exc:
            db.session.rollback()
            if getattr(exc.orig, 'pgcode', None) == '23505':
                return "Track already saved by this user", 409
            return "Invalid saved track data or track ID", 400
        except sqlalchemy.exc.DataError:
            db.session.rollback()
            return "Invalid saved track data", 400
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to save track")
            return "Unable to save track", 500

        


@saved_track_route.route('/saved_tracks/<uuid:saved_track_id>', methods=['GET', 'PATCH', 'DELETE'])
def saved_track_detail(saved_track_id):
    if request.method == 'GET':
        # TODO: Retrieve a saved track belonging to the authenticated user.
        try:
            saved = db.session.get(SavedTracks, saved_track_id)
            if saved is None:
                return "Saved track not found", 404
            return jsonify(record_dict(saved, RESPONSE_FIELDS)), 200
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to retrieve saved track")
            return "Unable to retrieve saved track", 500

    if request.method == 'PATCH':
        # TODO: Validate and apply allowed updates to the saved track.
        pass

    if request.method == 'DELETE':
        # TODO: Remove a saved track belonging to the authenticated user.
        pass
