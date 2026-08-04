from models.extensions import db
from sqlalchemy import String, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import uuid

class Tracks(db.Model):
    __tablename__ = "tracks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    era_id = Column(UUID(as_uuid=True), ForeignKey("eras.id"), nullable=False)
    title = Column(String, nullable=False)
    notes = Column(String)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())