from typing import List

from pydantic import BaseModel, Field

from opengenes.presenters.disease import DiseaseShort, DiseaseCategories
from opengenes.presenters.expression import Expression
from opengenes.presenters.functional_cluster import FunctionalCluster
from opengenes.presenters.functions import Function
from opengenes.presenters.human_protein_atlas import HumanProteinAtlas
from opengenes.presenters.origin import Origin, FamilyOrigin
from opengenes.presenters.researches import Researches


class GeneShort(BaseModel):
    id: int
    symbol: str
    name: str
    ncbiId: str
    uniprot: str
    origin: Origin
    familyOrigin: FamilyOrigin = Field(title="Family origin")
    homologueTaxon: str = Field(title="Homologue taxon")
    aliases: List[str]
    diseases: DiseaseShort
    functionalClusters: List[FunctionalCluster] = Field(title="Functional clusters")
    expressionChange: str = Field(title="Expression change")
    timestamp: int
    ensembl: str
    methylationCorrelation: str = Field(title="Methylation correlation")
    diseaseCategories: dict = Field(title="Disease categories")
    commentCause: dict = Field(title="Comment cause")


class Gene(BaseModel):
    id: int
    name: str
    symbol: str
    aliases: List[str]
    homologueTaxon: str = Field(title="Homologue taxon")
    origin: Origin
    familyOrigin: FamilyOrigin = Field(title="Family origin")
    diseases: DiseaseShort
    diseaseCategories: List[DiseaseCategories] = Field(title="Disease categories")
    ncbiId: str
    uniprot: str
    commentEvolution: str = Field(title="Comment evolution")
    commentFunction: str = Field(title="Comment function")
    descriptionNCBI: str
    descriptionOG: str
    commentCause: dict = Field(title="Comment cause")
    commentAging: str = Field(title="Comment aging")
    commentsReferenceLinks: dict = Field(title="Comment reference links")
    rating: bool
    functionalClusters: List[FunctionalCluster] = Field(title="Functional clusters")
    researches: Researches
    expression: List[Expression]
    functions: List[Function]
    proteinClasses: List[str] = Field(title="Protein classes")
    expressionChange: int = Field(title="Expression change")
    band: str
    locationStart: str = Field(title="Location start")
    locationEnd: str = Field(title="Location end")
    orientation: str
    accPromoter: str
    accOrf: str
    accCds: str
    terms: dict
    orthologs: dict
    why: List[str]
    timestamp: int
    human_protein_atlas: HumanProteinAtlas = Field(title="Human protein atlas")
    ensembl: str
    methylationCorrelation: str = Field(title="Methylation correlation")
