from flask import Blueprint, current_app, jsonify, request
import sqlalchemy
from models.eras import Eras
from models.extensions import db


eras_routes = Blueprint("eras_routes", __name__)

@eras_routes.route('/eras', methods= ['GET', 'POST'])
def eras():
    if request.method == 'GET':
        eras_data = db.session.scalars(db.select(Eras)).all()
        eras_list = [{"name": era.name, "artist_id": era.artist_id, "user_id": era.user_id,"id": era.id, "created_at": era.created_at} for era in eras_data]
        return jsonify(eras_list), 200
    elif request.method == 'POST':
        era_info = request.json
        if era_info.get("name") is None or era_info.get("user_id") is None or era_info.get("artist_id") is None:
            return "Missing required field(s)", 400
        else:
            era = Eras(name= era_info["name"], user_id = era_info["user_id"],artist_id = era_info["artist_id"])
            db.session.add(era)
            try:
                db.session.commit() 
                era_data = {"id": era.id, "name": era.name, "user_id": era.user_id, "artist_id": era.artist_id, "created_at": era.created_at}
                return jsonify(era_data), 201
            except sqlalchemy.exc.IntegrityError:
                db.session.rollback()
                return "Invalid Artist_Id, please try again", 400

@eras_routes.route('/eras/<uuid:era_id>', methods= ['PATCH', 'DELETE'])
def era_detail(era_id):
    if request.method == "DELETE":
        try:
            selected_era = db.session.get(Eras, era_id)
            if selected_era is None:
                return "Error, selected_era is not in DB"
            db.session.delete(selected_era)
            db.session.commit()
        except sqlalchemy.exc.DataError:
            db.session.rollback()
            return "Data Error", 400
    elif request.method == "PATCH":
        if not request.is_json:
            return "Request must contain JSON", 415
        r_update = request.get_json()
        if not isinstance(r_update, dict):
            return "JSON body must be an object", 400
        if "name" in r_update:
            if not isinstance(r_update["name"], str) or not r_update["name"].strip():
                return "Name must be a non-empty string", 400

        try:
            updated_era = db.session.get(Eras, era_id)
            if updated_era is None:
                return "Era not found", 404

            if "name" in r_update:
                updated_era.name = r_update["name"].strip()

            db.session.commit()
            return jsonify({
                "id": updated_era.id,
                "name": updated_era.name,
                "artist_id": updated_era.artist_id,
                "user_id": updated_era.user_id,
                "created_at": updated_era.created_at
            }), 200
        except (sqlalchemy.exc.DataError, sqlalchemy.exc.IntegrityError):
            db.session.rollback()
            return "Invalid era data", 400
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to update era")
            return "Unable to update era", 500


