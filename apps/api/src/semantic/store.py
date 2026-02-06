from __future__ import annotations

from typing import List

from sqlalchemy import JSON, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from persistence.db import Base, SessionLocal
from semantic.models import Dimension, Metric


class MetricORM(Base):
    __tablename__ = "semantic_metrics"

    name: Mapped[str] = mapped_column(String(128), primary_key=True)
    definition: Mapped[str] = mapped_column(String(1024))
    granularity: Mapped[str | None] = mapped_column(String(64))
    default_filters: Mapped[dict] = mapped_column(JSON, default=dict)
    version: Mapped[str | None] = mapped_column(String(32))
    available_dimensions: Mapped[list] = mapped_column(JSON, default=list)
    owner: Mapped[str | None] = mapped_column(String(64))


class DimensionORM(Base):
    __tablename__ = "semantic_dimensions"

    name: Mapped[str] = mapped_column(String(128), primary_key=True)
    description: Mapped[str] = mapped_column(String(256))
    hierarchy: Mapped[str | None] = mapped_column(String(256))
    primary_key: Mapped[str | None] = mapped_column(String(128))
    joinable_to: Mapped[list] = mapped_column(JSON, default=list)


SEED_METRICS = [
    Metric(
        name="active_users",
        definition="Distinct users active in the selected period",
        granularity="daily",
        default_filters={"status": "active"},
        version="v1",
        available_dimensions=["date", "country", "channel"],
        owner="growth",
    ),
    Metric(
        name="conversion_rate",
        definition="Purchases / sessions",
        granularity="weekly",
        default_filters={"traffic": "all"},
        version="v2",
        available_dimensions=["date", "channel", "device"],
        owner="product",
    ),
]

SEED_DIMENSIONS = [
    Dimension(
        name="date",
        description="Calendar date",
        hierarchy="year > quarter > month > day",
        primary_key="date_id",
        joinable_to=["active_users", "conversion_rate"],
    ),
    Dimension(
        name="country",
        description="User country",
        hierarchy="region > country",
        primary_key="country_code",
        joinable_to=["active_users"],
    ),
]


def _session() -> Session:
    return SessionLocal()


def ensure_seed() -> None:
    with _session() as session:
        existing = session.execute(select(MetricORM).limit(1)).scalar_one_or_none()
        if not existing:
            for metric in SEED_METRICS:
                session.add(
                    MetricORM(
                        name=metric.name,
                        definition=metric.definition,
                        granularity=metric.granularity,
                        default_filters=metric.default_filters,
                        version=metric.version,
                        available_dimensions=metric.available_dimensions,
                        owner=metric.owner,
                    )
                )
            for dim in SEED_DIMENSIONS:
                session.add(
                    DimensionORM(
                        name=dim.name,
                        description=dim.description,
                        hierarchy=dim.hierarchy,
                        primary_key=dim.primary_key,
                        joinable_to=dim.joinable_to,
                    )
                )
            session.commit()


def list_metrics() -> List[Metric]:
    ensure_seed()
    with _session() as session:
        rows = session.execute(select(MetricORM)).scalars().all()
        return [
            Metric(
                name=row.name,
                definition=row.definition,
                granularity=row.granularity,
                default_filters=row.default_filters,
                version=row.version,
                available_dimensions=row.available_dimensions,
                owner=row.owner,
            )
            for row in rows
        ]


def list_dimensions() -> List[Dimension]:
    ensure_seed()
    with _session() as session:
        rows = session.execute(select(DimensionORM)).scalars().all()
        return [
            Dimension(
                name=row.name,
                description=row.description,
                hierarchy=row.hierarchy,
                primary_key=row.primary_key,
                joinable_to=row.joinable_to,
            )
            for row in rows
        ]
