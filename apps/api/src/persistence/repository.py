from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from persistence.db import SessionLocal
from persistence.models import TaskORM, TaskRecord
from shared.types import TaskResult, TaskSpec


class TaskRepository:
    def __init__(self) -> None:
        self._session_factory = SessionLocal

    def _session(self) -> Session:
        return self._session_factory()

    def create(self, spec: TaskSpec) -> TaskRecord:
        with self._session() as session:
            task = TaskORM(
                id=spec.id,
                question=spec.question,
                created_at=spec.created_at,
                status=spec.status,
                meta=spec.meta,
                labels=spec.labels,
                result=None,
            )
            session.add(task)
            session.commit()
        return TaskRecord(spec=spec, result=None)

    def set_result(self, task_id: str, result: TaskResult) -> None:
        with self._session() as session:
            task = session.get(TaskORM, task_id)
            if not task:
                return
            task.result = result.model_dump(mode="json")
            task.status = "completed"
            session.commit()

    def get(self, task_id: str) -> Optional[TaskRecord]:
        with self._session() as session:
            task = session.get(TaskORM, task_id)
            if not task:
                return None
            spec = TaskSpec(
                id=task.id,
                question=task.question,
                created_at=task.created_at,
                status=task.status,
                meta=task.meta,
                labels=task.labels or [],
            )
            result = TaskResult(**task.result) if task.result else None
            return TaskRecord(spec=spec, result=result)

    def list(self, limit: int = 50) -> List[TaskRecord]:
        with self._session() as session:
            rows = session.execute(
                select(TaskORM).order_by(TaskORM.created_at.desc()).limit(limit)
            ).scalars().all()
            records: List[TaskRecord] = []
            for task in rows:
                spec = TaskSpec(
                    id=task.id,
                    question=task.question,
                    created_at=task.created_at,
                    status=task.status,
                    meta=task.meta,
                    labels=task.labels or [],
                )
                result = TaskResult(**task.result) if task.result else None
                records.append(TaskRecord(spec=spec, result=result))
            return records

    def delete(self, task_id: str) -> bool:
        with self._session() as session:
            task = session.get(TaskORM, task_id)
            if not task:
                return False
            session.delete(task)
            session.commit()
            return True
