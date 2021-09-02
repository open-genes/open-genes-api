from typing import List

from pydantic import BaseModel

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
    familyOrigin: FamilyOrigin
    homologueTaxon: str
    aliases: List[str]
    diseases: DiseaseShort
    functionalClusters: List[FunctionalCluster]
    expressionChange: str
    timestamp: int
    ensembl: str
    methylationCorrelation: str
    diseaseCategories: dict
    commentCause: dict


class Gene(BaseModel):
    id: int
    name: str
    symbol: str
    aliases: List[str]
    homologueTaxon: str
    origin: Origin
    familyOrigin: FamilyOrigin
    diseases: DiseaseShort
    diseaseCategories: List[DiseaseCategories]
    ncbiId: str
    uniprot: str
    commentEvolution: str
    commentFunction: str
    descriptionNCBI: str
    descriptionOG: str
    commentCause: dict
    commentAging: str
    commentsReferenceLinks: dict
    rating: bool
    functionalClusters: List[FunctionalCluster]
    researches: Researches
    expression: List[Expression]
    functions: List[Function]
    proteinClasses: List[str]
    expressionChange: int
    band: str
    locationStart: str
    locationEnd: str
    orientation: str
    accPromoter: str
    accOrf: str
    accCds: str
    terms: dict
    orthologs: dict
    why: List[str]
    timestamp: int
    human_protein_atlas: HumanProteinAtlas
    ensembl: str
    methylationCorrelation: str
