from typing import List

from pydantic import BaseModel, Field


class HumanProteinAtlas(BaseModel):
    Gene: str
    GeneSynonym: List[str] = Field(title="Gene synonym")
    Ensembl: str  = Field(title="Ensembl id")
    GeneDescription: str = Field(title="Gene description")
    Uniprot: List[str]
    Chromosome: str
    Position: str
    ProteinClass: List[str] = Field(title="Protein classes", description="see https://www.proteinatlas.org/humanproteome/proteinclasses")
    BiologicalProcess: List[str] = Field(title="Biological process (UniProt)", description="Separate classification, but corresponds with Gene Ontology")
    MolecularFunction: List[str] = Field(title="Molecular function (UniProt)", description="Separate classification, but corresponds with Gene Ontology")
    SubcellularLocation: List[str]
    SubcellularMainLocation: List[str]
    SubcellularAdditionalLocation: List[str]
    DiseaseInvolvement: List[str] = Field(title="Disease involvement", description="The genes group the gene belongs to associated with a certain type of diseases")
    Evidence: str = Field(title="Evidence", description="Example: Evidence at protein level")
