from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import Optional


@dataclass
class Origin:
    id: Optional[int]
    phylum: Optional[str] = Field(
        title="An organism in which a homologue of a human gene has appeared",
        default=None,
    )
    age: Optional[str] = Field(title="Gene evolutionary age", description="A range of values can be specified.", default=None)
    order: Optional[int] = Field(title="Sorting order", description="A field is being used for sorting genes according to age.",
                       default=None)
