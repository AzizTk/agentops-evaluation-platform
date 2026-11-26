"""SQLAlchemy persistence for run traces."""
from datetime import datetime
from sqlalchemy import DateTime, Float, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import settings
from .schemas import RunRecord

class Base(DeclarativeBase):
    pass

class RunRow(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    agent_name: Mapped[str] = mapped_column(String(120))
    question: Mapped[str] = mapped_column(Text)
    final_output: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float)
    payload: Mapped[str] = mapped_column(Text)

def make_engine(url: str | None = None):
    db_url = url or settings.database_url
    kwargs = {"connect_args": {"check_same_thread": False}} if db_url.startswith("sqlite") else {}
    return create_engine(db_url, future=True, **kwargs)

engine = make_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db(target_engine=None):
    Base.metadata.create_all(target_engine or engine)

def save_run(run: RunRecord, target_session_factory=SessionLocal):
    with target_session_factory() as session:
        session.merge(RunRow(id=run.id, agent_name=run.agent_name, question=run.question,
            final_output=str(run.final_output), status=run.status, started_at=run.started_at,
            completed_at=run.completed_at, duration_ms=run.duration_ms, payload=run.model_dump_json()))
        session.commit()

def get_run(run_id: str, target_session_factory=SessionLocal):
    with target_session_factory() as session:
        row = session.get(RunRow, run_id)
        return RunRecord.model_validate_json(row.payload) if row else None

def list_runs(limit: int = 50, target_session_factory=SessionLocal):
    with target_session_factory() as session:
        rows = session.scalars(select(RunRow).order_by(RunRow.started_at.desc()).limit(limit)).all()
        return [RunRecord.model_validate_json(row.payload) for row in rows]
