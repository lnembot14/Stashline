from models.extensions import db
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid


class SavedTracks(db.Model):
    __tablename__ = "saved_tracks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), nullable=False)

    track_id = Column(UUID(as_uuid=True), ForeignKey('tracks.id'), nullable = False)

    saved_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "track_id", name="uq_saved_tracks_user_track"),
    )