from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import Optional


@dataclass
class ProteinClass:
    id: Optional[int]
    name: Optional[str] = Field()
