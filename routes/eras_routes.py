from flask import Blueprint, jsonify, request
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
            


