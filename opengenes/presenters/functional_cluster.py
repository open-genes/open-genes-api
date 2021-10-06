from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import Optional

@dataclass
class FunctionalCluster:
    id: Optional[int]
    name: Optional[str] = Field(title="Name of the age-related process/system the gene involved in")
