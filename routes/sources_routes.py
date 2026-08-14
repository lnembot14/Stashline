from flask import Blueprint, jsonify, request
import sqlalchemy
from models.sources import Source
from models.extensions import db


source_route = Blueprint("source_route", __name__)

@source_route.route('/sources', methods= ['POST', 'GET'])
def source():
    if request.method == 'GET':
        source_data = db.session.scalars(db.select(Source)).all()
        source_list = [{"id": source.id, "track_id": source.track_id, "platform": source.platform, "url": source.url, "quality": source.quality, "upload_date": source.upload_date, "user_id": source.user_id, "created_at": source.created_at} for source in source_data]
        return jsonify(source_list), 200
    elif request.method == 'POST':
        sources_db = request.json
        if sources_db.get("user_id") is None or sources_db.get("url") is None or sources_db.get("track_id") is None or sources_db.get("platform") is None:
            return "Missing required field(s)", 400
        else:
            source_info = Source(user_id = sources_db["user_id"], url = sources_db["url"], track_id = sources_db["track_id"], platform = sources_db["platform"] )
            db.session.add(source_info)
            try:
                db.session.commit()
                source_dict = {"id": source_info.id, "url": source_info.url, "track_id": source_info.track_id, "platform": source_info.platform, "quality": source_info.quality, "upload_date": source_info.upload_date, "created_at": source_info.created_at}
                return jsonify(source_dict), 200
            except sqlalchemy.exc.IntegrityError:
                db.session.rollback()
                return "Invalid entry try again", 400
