"""Shared request validation for the JSON routes."""

from datetime import datetime, timezone
from uuid import UUID

from flask import request
from werkzeug.exceptions import BadRequest, UnsupportedMediaType


def read_json(fields, required=()):
    """Validate allowed fields and return values ready for the model."""
    if not request.is_json:
        raise UnsupportedMediaType("Request must contain JSON")
    data = request.get_json()
    if not isinstance(data, dict) or not data:
        raise BadRequest("JSON body must be a non-empty object")

    unknown = data.keys() - fields.keys()
    if unknown:
        raise BadRequest(f"Unsupported field(s): {', '.join(sorted(unknown))}")
    missing = set(required) - data.keys()
    if missing:
        raise BadRequest(f"Missing required field(s): {', '.join(sorted(missing))}")

    for field, value in data.items():
        field_type = fields[field]
        if field_type in ("optional_text", "date") and value is None:
            continue
        if not isinstance(value, str):
            raise BadRequest(f"{field} must be a string")

        if field_type in ("text", "optional_text"):
            if field_type == "text" and not value.strip():
                raise BadRequest(f"{field} must be a non-empty string")
            data[field] = value.strip()
        elif field_type == "uuid":
            try:
                data[field] = UUID(value)
            except ValueError:
                raise BadRequest(f"{field} must be a valid UUID") from None
        elif field_type == "date":
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                # Models use timezone-naive timestamps; store offsets as UTC.
                if parsed.tzinfo is not None:
                    parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
                data[field] = parsed
            except (ValueError, OverflowError):
                raise BadRequest(f"{field} must be an ISO 8601 date string or null") from None
    return data


def record_dict(record, fields):
    return {field: getattr(record, field) for field in fields}
