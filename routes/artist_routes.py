from flask import Blueprint, jsonify, request
from models.artists import Artists
from models.extensions import db
import requests


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
    selected_artist = db.session.get(Artists, artist_id)
    return selected_artist

    
