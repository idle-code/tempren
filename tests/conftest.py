from pathlib import Path

import pytest


@pytest.fixture
def nonexistent_path() -> Path:
    return Path("nonexistent", "path")
