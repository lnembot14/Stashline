from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
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
                source_dict = {"user_id": source_info.user_id, "id": source_info.id, "url": source_info.url, "track_id": source_info.track_id, "platform": source_info.platform, "quality": source_info.quality, "upload_date": source_info.upload_date, "created_at": source_info.created_at}
                return jsonify(source_dict), 200
            except sqlalchemy.exc.IntegrityError:
                db.session.rollback()
                return "Invalid entry try again", 400

@source_route.route('/sources/<uuid:source_id>', methods= ['PATCH', 'DELETE'])
def sources_detail(source_id):
    if request.method == "DELETE":
        selected_source = db.session.get(Source, source_id)
        db.session.delete(selected_source)
        db.session.commit()
        return "Successful deletion"
    elif request.method == "PATCH":
        if not request.is_json:
            return "Request must contain JSON", 415
        updates = request.get_json()
        if not isinstance(updates, dict) or not updates:
            return "JSON body must be a non-empty object", 400

        editable_fields = {"platform", "url", "quality", "upload_date"}
        if updates.keys() - editable_fields:
            return "Only platform, url, quality, and upload_date can be updated", 400

        for field in ("platform", "url"):
            if field in updates:
                if not isinstance(updates[field], str) or not updates[field].strip():
                    return f"{field} must be a non-empty string", 400
                updates[field] = updates[field].strip()

        if "quality" in updates and updates["quality"] is not None:
            if not isinstance(updates["quality"], str):
                return "quality must be a string or null", 400
            updates["quality"] = updates["quality"].strip()

        if "upload_date" in updates and updates["upload_date"] is not None:
            if not isinstance(updates["upload_date"], str):
                return "upload_date must be an ISO 8601 date string or null", 400
            try:
                upload_date = datetime.fromisoformat(updates["upload_date"].replace("Z", "+00:00"))
            except ValueError:
                return "upload_date must be an ISO 8601 date string or null", 400
            # The model stores timestamps without a timezone; normalize offsets to UTC.
            if upload_date.tzinfo is not None:
                upload_date = upload_date.astimezone(timezone.utc).replace(tzinfo=None)
            updates["upload_date"] = upload_date

        try:
            selected_source = db.session.get(Source, source_id)
            if selected_source is None:
                return "Source not found", 404

            for field, value in updates.items():
                setattr(selected_source, field, value)

            db.session.commit()
            return jsonify({
                "id": selected_source.id,
                "track_id": selected_source.track_id,
                "platform": selected_source.platform,
                "url": selected_source.url,
                "quality": selected_source.quality,
                "upload_date": selected_source.upload_date,
                "user_id": selected_source.user_id,
                "created_at": selected_source.created_at
            }), 200
        except (sqlalchemy.exc.DataError, sqlalchemy.exc.IntegrityError):
            db.session.rollback()
            return "Invalid source data", 400
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to update source")
            return "Unable to update source", 500
