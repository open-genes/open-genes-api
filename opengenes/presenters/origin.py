from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class Origin:
    id: int
    phylum: str = Field(
        title="An organism in which a homologue of a human gene has appeared",
        default=None,
    )
    age: str = Field(title="Gene evolutionary age", description="A range of values can be specified.", default=None)
    order: int = Field(title="Sorting order", description="A field is being used for sorting genes according to age.",
                       default=None)

    def __init__(
        self,
        id,
        name_phylo=None,
        order=None,
        name_mya=None,
        **kwargs
    ):
        self.id = id
        self.age = name_mya
        self.phylum = name_phylo
        self.order = order
