from flask import Blueprint, jsonify, request
from models.artists import Artists
from models.extensions import db
import requests
import sqlalchemy


artist_route = Blueprint("artist_route", __name__)

@artist_route.route('/artists', methods= ['GET', 'POST'])
def artists():
    if request.method == 'GET':
        artists = db.session.scalars(db.select(Artists)).all()
        artist_list = [{"id": artist.id, "name": artist.name, "user_id": artist.user_id, "created_at": artist.created_at} for artist in artists]
        return jsonify(artist_list), 200 
    elif request.method == 'POST':
        artist_info = request.json
        artist = Artists(name = artist_info["name"], user_id = artist_info["user_id"])
        db.session.add(artist)
        db.session.commit()
        artist_data = {"id": artist.id, "name": artist.name, "user_id": artist.user_id, "created_at": artist.created_at}
        return jsonify(artist_data), 201

@artist_route.route('/artists/<artist_id>', methods = ["PATCH", "DELETE"])
def artist_detail(artist_id):
    if request.method == "DELETE":
        try:
            selected_artist = db.session.get(Artists, artist_id)
            if selected_artist is None:
                return "Artist not found", 404
            else:
                db.session.delete(selected_artist)
                db.session.commit() 
                return "Item deleted", 200  
        except sqlalchemy.exc.DataError:
            db.session.rollback()
            return "Data Error", 400
    elif request.method == "PATCH":
        try:

            if not request.is_json:
                 return "Request must contain JSON", 415
            updates = request.get_json()
            if not isinstance(updates, dict):
                    return "JSON body must be an object", 400
            
            updated_artist = db.session.get(Artists, artist_id)

            if updated_artist is None:
                return "Can't update artist not in DB", 404
            else:
                if "name" in updates:
                    if not isinstance(updates["name"], str) or not updates["name"].strip():
                        return "Name must be a non-empty string", 400
                    updated_artist.name = updates["name"].strip()
                db.session.commit()
                return jsonify({
                    "id": updated_artist.id,
                    "name": updated_artist.name,
                    "user_id": updated_artist.user_id,
                    "created_at": updated_artist.created_at
                }), 200
        except sqlalchemy.exc.DataError:
                    db.session.rollback()
                    return "Data Error", 400

        