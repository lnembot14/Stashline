from models.extensions import db
from sqlalchemy import String, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

class Artists(db.Model):
    __tablename__ = "artists"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


