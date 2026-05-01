import uuid
from sqlalchemy import String, Integer, Float, JSON, ForeignKey, DateTime, Uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, Any, Dict
from datetime import datetime

from .database import Base

class Run(Base):
    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    agent_name: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String)
    input: Mapped[Dict[str, Any]] = mapped_column(JSON)
    output: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    share_token: Mapped[str] = mapped_column(String, unique=True, index=True)

    steps = relationship("Step", back_populates="run", cascade="all, delete-orphan")
    analysis = relationship("AnalysisCache", back_populates="run", uselist=False)

class Step(Base):
    __tablename__ = "steps"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"))
    step_index: Mapped[int] = mapped_column(Integer)
    step_type: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    input: Mapped[Dict[str, Any]] = mapped_column(JSON)
    output: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String)
    started_at: Mapped[datetime] = mapped_column(DateTime)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    step_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)

    run = relationship("Run", back_populates="steps")

class AnalysisCache(Base):
    __tablename__ = "analysis_cache"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), unique=True)
    root_cause: Mapped[str] = mapped_column(String)
    fix_suggestion: Mapped[str] = mapped_column(String)
    fix_code_hint: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    confidence: Mapped[float] = mapped_column(Float)
    failure_category: Mapped[str] = mapped_column(String)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime)
    gemini_model: Mapped[str] = mapped_column(String)

    run = relationship("Run", back_populates="analysis")
