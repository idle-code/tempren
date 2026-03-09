from pathlib import Path
from typing import Any

from tempren.primitives import Tag


class TestTag(Tag):
    """Test tag without package"""

    require_context = False

    def process(self, path: Path, context: str | None) -> Any:
        return ""
