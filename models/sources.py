from models.extensions import db
from sqlalchemy import String, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import uuid


class Source(db.Model):
    __tablename__ = "sources"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"), nullable=False)
    platform = Column(String, nullable=False)
    url = Column(String, nullable=False)
    quality = Column(String, nullable=False)
    upload_date = Column(DateTime)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())