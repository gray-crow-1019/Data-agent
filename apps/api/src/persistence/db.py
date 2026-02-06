from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from settings import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    from persistence.models import TaskORM
    from semantic.store import DimensionORM, MetricORM

    Base.metadata.create_all(bind=engine)


def get_task_repo():
    from persistence.repository import TaskRepository

    return TaskRepository()
