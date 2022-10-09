from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class Timestamp:
    created: Optional[int] = Field(title="Unix time when gene was added")
    changed: Optional[int] = Field(title="Unix time of the latest changes")
