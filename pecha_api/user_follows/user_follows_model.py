from sqlalchemy import Column, DateTime, UUID, ForeignKey, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from ..db.database import Base
from uuid import uuid4
from _datetime import datetime
import _datetime


class UserFollow(Base):
    __tablename__ = "user_follows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc))

    # Optional relationships (no back_populates on Users)
    follower = relationship("Users", foreign_keys=[follower_id])
    following = relationship("Users", foreign_keys=[following_id])

    __table_args__ = (
        # Prevent self-following and duplicates
        CheckConstraint("follower_id != following_id", name="no_self_follow"),
        UniqueConstraint("follower_id", "following_id", name="unique_follow"),
        # Indexes for performance
        Index("idx_user_follows_follower", "follower_id"),
        Index("idx_user_follows_following", "following_id"),
        Index("idx_user_follows_created", "created_at"),
    )