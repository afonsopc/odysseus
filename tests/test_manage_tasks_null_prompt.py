"""Regression: manage_tasks create must not crash when prompt is explicitly null."""
import asyncio
import json
import types as _types

import pytest

sqlalchemy = pytest.importorskip("sqlalchemy")
if not isinstance(sqlalchemy, _types.ModuleType):
    pytest.skip("sqlalchemy is stubbed in this environment", allow_module_level=True)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import core.database as _db
from core.database import Base

if type(Base).__name__ == "MagicMock":
    pytest.skip("core.database is stubbed — run this file in isolation", allow_module_level=True)

from src.tool_implementations import do_manage_tasks


def test_create_action_task_with_null_prompt(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    monkeypatch.setattr(_db, "SessionLocal", sessionmaker(bind=engine))

    content = json.dumps({
        "action": "create",
        "task_type": "action",
        "action_name": "tidy_documents",
        "prompt": None,             # present but null — used to crash on None[:50]
        "trigger_type": "event",    # avoids schedule/next_run computation
        "trigger_event": "session_created",
    })
    result = asyncio.run(do_manage_tasks(content, owner="alice"))

    assert result.get("exit_code") == 0, result
    # With no name and a null prompt, the name falls back to action_name.
    assert "tidy_documents" in result.get("response", "")
