from models.extensions import db
from sqlalchemy import String, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import uuid



class Eras(db.Model):
    __tablename__ = "eras"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=False)
    name = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
