from typing import List, Optional, Dict

from pydantic import Field
from pydantic.dataclasses import dataclass
from opengenes.db.dao import GeneDAO, DiseaseDAO, FunctionalClusterDAO, CommentCauseDAO

from opengenes.presenters.disease import DiseaseShort, DiseaseCategories
from opengenes.presenters.expression import Expression
from opengenes.presenters.functional_cluster import FunctionalCluster
from opengenes.presenters.human_protein_atlas import HumanProteinAtlas
from opengenes.presenters.aging_mechanism import AgingMechanism
from opengenes.presenters.timestamp import Timestamp
from opengenes.presenters.origin import Origin
from opengenes.presenters.researches import Researches
from opengenes.presenters.comment_cause import CommentCause
from json import loads


BAD_CLUSTER = {"id": None, "name": None}


@dataclass
class GeneShort:
    id: int
    symbol: str = Field(title="Gene symbol (HGNC)", default=None)
    name: str = Field(title="Gene name", default=None)
    ncbiId: str = Field(title="Entrez Gene id", default=None)
    uniprot: str = Field(title="UniProt id", default=None)
    origin: Optional[Origin] = Field(title="Gene evolutionary origin", default=None)
    familyOrigin: Optional[Origin] = Field(title="Gene family evolutionary origin")
    homologueTaxon: Optional[str] = Field(title="An organism the gene is conservative in")
    aliases: List[str] = Field(title="Gene symbols in the other nomenclatures")
    diseases: DiseaseShort = Field(title="Association with diseases (eDGAR)")
    functionalClusters: List[FunctionalCluster] = Field(title="Age-related processes/systems the gene involved in")
    expressionChange: str = Field(
        title="Age-dependent changes of gene expression",
        description="Designations: \n0 — no data \n1 — decreases\n2 — increases\n3 — mixed"
    )
    timestamp: int = Field(title="Unix time of the latest changes")
    ensembl: str = Field(title="Ensembl id")
    methylationCorrelation: str = Field(title="Whether gene methylation changes with age (according to Horvath's epigenetic clock)")
    diseaseCategories: dict = Field(title="Disease categories (ICD)")
    commentCause: dict = Field(title="Gene selection criteria")


@dataclass
class Gene:
    id: int
    name: str = Field(title="Gene name")
    symbol: str = Field(title="Gene symbol (HGNC)")
    aliases: List[str] = Field(title="Gene symbols in the other nomenclatures")
    homologueTaxon: str = Field(title="An organism the gene is conservative in")
    origin: Origin = Field(title="Gene evolutionary origin")
    familyOrigin: Origin = Field(title="Gene family evolutionary origin")
    diseases: DiseaseShort = Field(title="Association with diseases (eDGAR)")
    diseaseCategories: List[DiseaseCategories] = Field(title="Disease categories")
    ncbiId: str = Field(title="Entrez Gene id")
    uniprot: str = Field(title="UniProt id")
    commentEvolution: str = Field(title="Gene evolution summary")
    proteinDescriptionOpenGenes: str = Field(title="Protein description by Open Genes")
    descriptionNCBI: str = Field(title="Gene description (NCBI)")
    proteinDescriptionUniProt: str = Field(title="Protein description (UniProt)")
    commentCause: dict = Field(title="Gene selection criteria")
    functionalClusters: List[FunctionalCluster] = Field(title="Age-related processes/systems the gene involved in")
    agingMechanisms: List[AgingMechanism] = Field(title="Aging mechanism the gene involved in")
    researches: Researches = Field(title="Researches", description="Researches confirming the association of the gene with life expectancy and aging")
    expression: List[Expression] = Field(title="Gene expression in organs and tissues (NCBI)")
    proteinClasses: List[str] = Field(title="Protein classes", description="Protein classification by their function")
    expressionChange: str = Field(
        title="Age-dependent changes of gene expression",
        description="Designations: \n0 — no data \n1 — decreases\n2 — increases\n3 — mixed"
    )
    band: str = Field(title="Location on chromosome — cytogenetic band")
    locationStart: str = Field(title="Location on chromosome — start")
    locationEnd: str = Field(title="Location on chromosome — end")
    orientation: str = Field(title="Location on chromosome — Plus or minus strand")
    accPromoter: str = Field(title="Location on chromosome — Promoter")
    accOrf: str = Field(title="Location on chromosome — Open Reading Frame")
    accCds: str = Field(title="Location on chromosome — CoDing Sequence")
    terms: dict = Field(title="GO terms (Gene Ontology)")
    orthologs: dict = Field(title="Gene orthologs")
    timestamp: Timestamp = Field(title="Unix time of the latest changes")
    human_protein_atlas: HumanProteinAtlas = Field(title="Data parsed from Human Protein Atlas")
    ensembl: str = Field(title="Ensembl id")
    methylationCorrelation: str = Field(
        title="Horvath's epigenetic clock",
        description="Whether gene methylation changes with age (according to Horvath's epigenetic clock)"
    )
