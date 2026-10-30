from flask import Blueprint, current_app, jsonify, request
import sqlalchemy
from models.artists import Artists
from models.extensions import db
from routes.validation import read_json, record_dict


artist_route = Blueprint("artist_route", __name__)

# PATCH may change these fields; POST also accepts ownership and parent IDs.
EDITABLE_FIELDS = {'name': 'text'}
CREATE_FIELDS = {**EDITABLE_FIELDS, **{'user_id': 'text'}}
RESPONSE_FIELDS = ('id', 'name', 'user_id', 'created_at')


@artist_route.route('/artists', methods=['GET', 'POST'])
def artists():
    if request.method == 'GET':
        records = db.session.scalars(db.select(Artists)).all()
        return jsonify([record_dict(record, RESPONSE_FIELDS) for record in records]), 200

    values = read_json(CREATE_FIELDS, required=('name', 'user_id'))
    try:
        record = Artists(**values)
        db.session.add(record)
        db.session.commit()
        return jsonify(record_dict(record, RESPONSE_FIELDS)), 201
    except (sqlalchemy.exc.DataError, sqlalchemy.exc.IntegrityError):
        db.session.rollback()
        return "Invalid artist data or parent ID", 400
    except sqlalchemy.exc.SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to create artist")
        return "Unable to create artist", 500


@artist_route.route('/artists/<uuid:artist_id>', methods=['GET', 'PATCH', 'DELETE'])
def artist_detail(artist_id):
    # Validate before making changes. Omitted fields keep their current values.
    if request.method == 'PATCH':
        updates = read_json(EDITABLE_FIELDS)

    try:
        record = db.session.get(Artists, artist_id)
        if record is None:
            return "Artist not found", 404

        if request.method == 'GET':
            return jsonify(record_dict(record, RESPONSE_FIELDS)), 200
        if request.method == 'DELETE':
            db.session.delete(record)
            db.session.commit()
            return "Artist deleted", 200

        for field, value in updates.items():
            setattr(record, field, value)
        db.session.commit()
        return jsonify(record_dict(record, RESPONSE_FIELDS)), 200
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        if request.method == 'DELETE':
            return "Cannot delete artist while other records reference it", 409
        return "Invalid artist data", 400
    except sqlalchemy.exc.DataError:
        db.session.rollback()
        return "Invalid artist data", 400
    except sqlalchemy.exc.SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to process artist request")
        return "Unable to process artist request", 500
