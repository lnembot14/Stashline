from flask import Blueprint, current_app, jsonify, request
import sqlalchemy
from models.sources import Source
from models.extensions import db
from routes.validation import read_json, record_dict


source_route = Blueprint("source_route", __name__)

# PATCH may change these fields; POST also accepts ownership and parent IDs.
EDITABLE_FIELDS = {'platform': 'text', 'url': 'text', 'quality': 'optional_text', 'upload_date': 'date'}
CREATE_FIELDS = {**EDITABLE_FIELDS, **{'user_id': 'text', 'track_id': 'uuid'}}
RESPONSE_FIELDS = ('id', 'track_id', 'platform', 'url', 'quality', 'upload_date', 'user_id', 'created_at')


@source_route.route('/sources', methods=['GET', 'POST'])
def source():
    if request.method == 'GET':
        records = db.session.scalars(db.select(Source)).all()
        return jsonify([record_dict(record, RESPONSE_FIELDS) for record in records]), 200

    values = read_json(CREATE_FIELDS, required=('platform', 'url', 'user_id', 'track_id'))
    try:
        record = Source(**values)
        db.session.add(record)
        db.session.commit()
        return jsonify(record_dict(record, RESPONSE_FIELDS)), 201
    except (sqlalchemy.exc.DataError, sqlalchemy.exc.IntegrityError):
        db.session.rollback()
        return "Invalid source data or parent ID", 400
    except sqlalchemy.exc.SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to create source")
        return "Unable to create source", 500


@source_route.route('/sources/<uuid:source_id>', methods=['GET', 'PATCH', 'DELETE'])
def sources_detail(source_id):
    # Validate before making changes. Omitted fields keep their current values.
    if request.method == 'PATCH':
        updates = read_json(EDITABLE_FIELDS)

    try:
        record = db.session.get(Source, source_id)
        if record is None:
            return "Source not found", 404

        if request.method == 'GET':
            return jsonify(record_dict(record, RESPONSE_FIELDS)), 200
        if request.method == 'DELETE':
            db.session.delete(record)
            db.session.commit()
            return "Source deleted", 200

        for field, value in updates.items():
            setattr(record, field, value)
        db.session.commit()
        return jsonify(record_dict(record, RESPONSE_FIELDS)), 200
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        if request.method == 'DELETE':
            return "Cannot delete source while other records reference it", 409
        return "Invalid source data", 400
    except sqlalchemy.exc.DataError:
        db.session.rollback()
        return "Invalid source data", 400
    except sqlalchemy.exc.SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to process source request")
        return "Unable to process source request", 500
