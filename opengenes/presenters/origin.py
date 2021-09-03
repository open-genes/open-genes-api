from pydantic import BaseModel


class Origin(BaseModel):
    id: int
    phylum: str
    age: str
    order: int


class FamilyOrigin(BaseModel):
    id: int
    phylum: str
    age: str
    order: int
