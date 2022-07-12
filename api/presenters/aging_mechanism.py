from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class AgingMechanism:
    id: Optional[int]
    name: Optional[str] = Field(title="Name of the aging mechanism the gene involved in")
