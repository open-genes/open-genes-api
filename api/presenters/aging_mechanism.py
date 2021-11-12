from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import Optional

@dataclass
class AgingMechanism:
    id: Optional[int]
    name: Optional[str] = Field(title="Name of the aging mechanism the gene involved in")
