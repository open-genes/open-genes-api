from typing import List

from pydantic import BaseModel, Field


class HumanProteinAtlas(BaseModel):
    gene: str
    geneSynonym: List[str] = Field(title="Gene synonym")
    ensembl: str  = Field(title="Ensembl id")
    geneDescription: str = Field(title="Gene description")
    uniprot: List[str]
    chromosome: str
    position: str
