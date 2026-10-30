from flask import Blueprint, current_app, jsonify, request
import sqlalchemy
from models.eras import Eras
from models.extensions import db
from routes.validation import read_json, record_dict


eras_routes = Blueprint("eras_routes", __name__)

# PATCH may change these fields; POST also accepts ownership and parent IDs.
EDITABLE_FIELDS = {'name': 'text'}
CREATE_FIELDS = {**EDITABLE_FIELDS, **{'user_id': 'text', 'artist_id': 'uuid'}}
RESPONSE_FIELDS = ('id', 'name', 'artist_id', 'user_id', 'created_at')


@eras_routes.route('/eras', methods=['GET', 'POST'])
def eras():
    if request.method == 'GET':
        records = db.session.scalars(db.select(Eras)).all()
        return jsonify([record_dict(record, RESPONSE_FIELDS) for record in records]), 200

    values = read_json(CREATE_FIELDS, required=('name', 'user_id', 'artist_id'))
    try:
        record = Eras(**values)
        db.session.add(record)
        db.session.commit()
        return jsonify(record_dict(record, RESPONSE_FIELDS)), 201
    except (sqlalchemy.exc.DataError, sqlalchemy.exc.IntegrityError):
        db.session.rollback()
        return "Invalid era data or parent ID", 400
    except sqlalchemy.exc.SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to create era")
        return "Unable to create era", 500


@eras_routes.route('/eras/<uuid:era_id>', methods=['GET', 'PATCH', 'DELETE'])
def era_detail(era_id):
    # Validate before making changes. Omitted fields keep their current values.
    if request.method == 'PATCH':
        updates = read_json(EDITABLE_FIELDS)

    try:
        record = db.session.get(Eras, era_id)
        if record is None:
            return "Era not found", 404

        if request.method == 'GET':
            return jsonify(record_dict(record, RESPONSE_FIELDS)), 200
        if request.method == 'DELETE':
            db.session.delete(record)
            db.session.commit()
            return "Era deleted", 200

        for field, value in updates.items():
            setattr(record, field, value)
        db.session.commit()
        return jsonify(record_dict(record, RESPONSE_FIELDS)), 200
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        if request.method == 'DELETE':
            return "Cannot delete era while other records reference it", 409
        return "Invalid era data", 400
    except sqlalchemy.exc.DataError:
        db.session.rollback()
        return "Invalid era data", 400
    except sqlalchemy.exc.SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to process era request")
        return "Unable to process era request", 500
