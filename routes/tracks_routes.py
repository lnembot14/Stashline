from flask import Blueprint, current_app, jsonify, request
import sqlalchemy
from models.tracks import Tracks
from models.extensions import db
from routes.validation import read_json, record_dict


track_route = Blueprint("track_route", __name__)

# PATCH may change these fields; POST also accepts ownership and parent IDs.
EDITABLE_FIELDS = {'title': 'text', 'notes': 'optional_text'}
CREATE_FIELDS = {**EDITABLE_FIELDS, **{'user_id': 'text', 'era_id': 'uuid'}}
RESPONSE_FIELDS = ('id', 'era_id', 'title', 'notes', 'user_id', 'created_at')


@track_route.route('/tracks', methods=['GET', 'POST'])
def track():
    if request.method == 'GET':
        records = db.session.scalars(db.select(Tracks)).all()
        return jsonify([record_dict(record, RESPONSE_FIELDS) for record in records]), 200

    values = read_json(CREATE_FIELDS, required=('title', 'user_id', 'era_id'))
    try:
        record = Tracks(**values)
        db.session.add(record)
        db.session.commit()
        return jsonify(record_dict(record, RESPONSE_FIELDS)), 201
    except (sqlalchemy.exc.DataError, sqlalchemy.exc.IntegrityError):
        db.session.rollback()
        return "Invalid track data or parent ID", 400
    except sqlalchemy.exc.SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to create track")
        return "Unable to create track", 500


@track_route.route('/tracks/<uuid:track_id>', methods=['GET', 'PATCH', 'DELETE'])
def track_detail(track_id):
    # Validate before making changes. Omitted fields keep their current values.
    if request.method == 'PATCH':
        updates = read_json(EDITABLE_FIELDS)

    try:
        record = db.session.get(Tracks, track_id)
        if record is None:
            return "Track not found", 404

        if request.method == 'GET':
            return jsonify(record_dict(record, RESPONSE_FIELDS)), 200
        if request.method == 'DELETE':
            db.session.delete(record)
            db.session.commit()
            return "Track deleted", 200

        for field, value in updates.items():
            setattr(record, field, value)
        db.session.commit()
        return jsonify(record_dict(record, RESPONSE_FIELDS)), 200
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        if request.method == 'DELETE':
            return "Cannot delete track while other records reference it", 409
        return "Invalid track data", 400
    except sqlalchemy.exc.DataError:
        db.session.rollback()
        return "Invalid track data", 400
    except sqlalchemy.exc.SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to process track request")
        return "Unable to process track request", 500
