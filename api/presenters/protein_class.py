from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class ProteinClass:
    id: Optional[int]
    name: Optional[str] = Field()
