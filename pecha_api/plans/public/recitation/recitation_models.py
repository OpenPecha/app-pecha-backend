
from sqlalchemy import Column, Index, String, UUID, JSON
from uuid import uuid4
from pecha_api.db.database import Base


class Recitation(Base):
    __tablename__ = "recitation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    audio_url = Column(String(255), nullable=False)
    content = Column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_recitation_title", "title")
    )