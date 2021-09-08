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
    symbol: str = Field(title="Gene symbol (HGNC)")
    name: str = Field(title="Gene name")
    ncbiId: str = Field(title="Entrez Gene id")
    uniprot: str = Field(title="UniProt id")
    origin: Origin = Field(title="Gene evolutionary origin")
    familyOrigin: FamilyOrigin = Field(title="Gene family evolutionary origin")
    homologueTaxon: str = Field(title="An organism the gene is conservative in")
    aliases: List[str] = Field(title="Gene symbols in the other nomenclatures")
    diseases: DiseaseShort = Field(title="Association with diseases (eDGAR)")
    functionalClusters: List[FunctionalCluster] = Field(title="Age-related processes and systems the gene involved in")
    expressionChange: str = Field(title="Age-dependent changes of gene expression")
    timestamp: int = Field(title="Unix time of the latest changes")
    ensembl: str = Field(title="Ensembl id")
    methylationCorrelation: str = Field(title="Whether gene methylation changes with age (according to Horvath's epigenetic clock)")
    diseaseCategories: dict = Field(title="Disease categories (ICD)")
    commentCause: dict = Field(title="Gene selection criteria")


class Gene(BaseModel):
    id: int
    name: str = Field(title="Gene name")
    symbol: str = Field(title="Gene symbol (HGNC)")
    aliases: List[str] = Field(title="Gene symbols in the other nomenclatures")
    homologueTaxon: str = Field(title="An organism the gene is conservative in")
    origin: Origin = Field(title="Gene evolutionary origin")
    familyOrigin: FamilyOrigin = Field(title="Gene family evolutionary origin")
    diseases: DiseaseShort = Field(title="Association with diseases (eDGAR)")
    diseaseCategories: List[DiseaseCategories] = Field(title="Disease categories")
    ncbiId: str = Field(title="Entrez Gene id")
    uniprot: str = Field(title="UniProt id")
    commentEvolution: str = Field(title="Gene evolution summary")
    proteinDescriptionOpenGenes: str = Field(title="Protein description by Open Genes")
    descriptionNCBI: str = Field(title="Gene description (NCBI)")
    proteinDescriptionUniProt: str = Field(title="Protein description (UniProt)")
    commentCause: dict = Field(title="Gene selection criteria")
    functionalClusters: List[FunctionalCluster] = Field(title="Age-related processes and systems the gene involved in")
    researches: Researches = Field(title="Researches", description="Researches confirming the association of the gene with life expectancy and aging")
    expression: List[Expression] = Field(title="Gene expression in organs and tissues (NCBI)")
    functions: List[Function]
    proteinClasses: List[str] = Field(title="Protein classes (Human Protein Atlas)", description="Human Protein Atlas protein classification")
    expressionChange: int = Field(title="Age-dependent changes of gene expression")
    band: str = Field(title="Location on chromosome — cytogenetic band")
    locationStart: str = Field(title="Location on chromosome — start")
    locationEnd: str = Field(title="Location on chromosome — end")
    orientation: str = Field(title="Location on chromosome — Plus or minus strand")
    accPromoter: str = Field(title="Location on chromosome — Promoter")
    accOrf: str = Field(title="Location on chromosome — Open Reading Frame")
    accCds: str = Field(title="Location on chromosome — CoDing Sequence")
    terms: dict = Field(title="GO terms (Gene Ontology)")
    orthologs: dict = Field(title="Gene orthologs")
    timestamp: int = Field(title="Unix time of the latest changes")
    human_protein_atlas: HumanProteinAtlas = Field(title="Data parsed from Human Protein Atlas")
    ensembl: str = Field(title="Ensembl id")
    methylationCorrelation: str = Field(title="Horvath's epigenetic clock", description="Whether gene methylation changes with age (according to Horvath's epigenetic clock)")
