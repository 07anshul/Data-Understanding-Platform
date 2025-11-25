from alembic.ddl.base import ColumnName
from sqlalchemy import Column, Integer, String, DateTime, text, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

    files = relationship("File", back_populates="user")

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    original_name = Column(String, nullable=True)
    stored_name = Column(String, nullable=False, unique=True)
    size_bytes = Column(BigInteger, nullable=False)
    status = Column(String, nullable=False, default="uploaded")
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

    user = relationship("User", back_populates="files", lazy="joined")
