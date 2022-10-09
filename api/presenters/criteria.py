from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class Criteria:
    id: int
    name: Optional[str]
