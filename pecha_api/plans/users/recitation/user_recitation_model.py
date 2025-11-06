from sqlalchemy import Column, ForeignKey, Index, String, UUID, UniqueConstraint
from uuid import uuid4
from pecha_api.db.database import Base
from sqlalchemy.orm import relationship


class UserRecitation(Base):
    __tablename__ = "user_recitation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recitation_id = Column(UUID(as_uuid=True), ForeignKey('recitation.id', ondelete='CASCADE'), nullable=False)
    
    user = relationship('Users', backref='user_recitations')
    recitation = relationship('Recitation', backref='user_recitations')

    __table_args__ = (
        UniqueConstraint("user_id", "recitation_id", name="uq_user_recitation_user_recitation"),
        Index("idx_user_recitation_user_recitation_user", "user_id"),
        Index("idx_user_recitation_user_recitation_recitation", "recitation_id"),
    )