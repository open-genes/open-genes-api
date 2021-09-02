from typing import List

from pydantic import BaseModel


class HumanProteinAtlas(BaseModel):
    Gene: str
    GeneSynonym: List[str]
    Ensembl: str
    GeneDescription: str
    Uniprot: List[str]
    Chromosome: str
    Position: str
