from pydantic import BaseModel, Field


class Origin(BaseModel):
    id: int
    phylum: str = Field(
        title="An organism in which a homologue of a human gene has appeared",
        default=None,
    )
    age: str = Field(title="Gene evolutionary age", description="A range of values can be specified.", default=None)
    order: int = Field(title="Sorting order", description="A field is being used for sorting genes according to age.", default=None)


class FamilyOrigin(BaseModel):
    id: int
    phylum: str = Field(title="An organism in which a gene family has appeared", default=None)
    age: str  = Field(title="Gene family evolutionary age", description="A range of values can be specified.", default=None)
    order: int = Field(title="Sorting order", description="A field is being used for sorting gene families according to age.", default=None)
