from pathlib import Path
from typing import Any, Optional

from tempren.primitives import Tag


class TestTag(Tag):
    """Test tag without package"""

    require_context = False

    def process(self, path: Path, context: Optional[str]) -> Any:
        return ""
