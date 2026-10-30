from models.extensions import db
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid


class SavedTracks(db.Model):
    __tablename__ = "saved_tracks"

    # TODO: Define your primary key.
    # TODO: Add user_id for the authenticated user's UUID.
    # TODO: Add track_id as a foreign key to tracks.id.
    # TODO: Add saved_at with a database-generated timestamp.
    # TODO: Prevent duplicate saves for the same user and track.
