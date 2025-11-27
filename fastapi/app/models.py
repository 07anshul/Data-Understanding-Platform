from alembic.ddl.base import ColumnName
from sqlalchemy import Column, Integer, String, DateTime, Text, text, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, relationship
from app.db import Base

# Base = declarative_base()

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
    path = Column(String, nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String, nullable=True)
    status = Column(String, nullable=False, default="uploaded")
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

    user = relationship("User", back_populates="files", lazy="joined")
    jobs = relationship("Job", back_populates="file")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"),nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    model_version = Column(String, nullable=True)
    status = Column(String, nullable=False, default="queued")
    progress = Column(Integer, nullable=False, default=0)
    result_path = Column(Integer, nullable=True)
    logs = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    file = relationship("File")

