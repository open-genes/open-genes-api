from typing import List, Optional, Dict

from pydantic import Field
from pydantic.dataclasses import dataclass
from opengenes.db.dao import GeneDAO, DiseaseDAO, FunctionalClusterDAO, CommentCauseDAO

from opengenes.presenters.disease import DiseaseShort, DiseaseCategories
from opengenes.presenters.expression import Expression
from opengenes.presenters.functional_cluster import FunctionalCluster
from opengenes.presenters.human_protein_atlas import HumanProteinAtlas
from opengenes.presenters.origin import Origin
from opengenes.presenters.researches import Researches
from opengenes.presenters.comment_cause import CommentCause


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
    diseases: Optional[Dict] = Field(title="Association with diseases (eDGAR)")
    functionalClusters: Optional[List[FunctionalCluster]] = Field(title="Age-related processes/systems the gene "
                                                                        "involved in")
    expressionChange: int = Field(title="Age-dependent changes of gene expression")
    timestamp: Optional[int] = Field(title="Unix time of the latest changes")
    ensembl: Optional[str] = Field(title="Ensembl id")
    methylationCorrelation: Optional[str] = Field(title="Whether gene methylation changes with age (according to "
                                                        "Horvath's epigenetic clock)")
    diseaseCategories: Optional[dict] = Field(title="Disease categories (ICD)")
    commentCause: dict = Field(title="Gene selection criteria")

    def __init__(
        self,
        id,
        symbol,
        name,
        ncbi_id,
        uniprot,
        phylum_id,
        family_phylum_id,
        taxon_id,
        aliases,
        expressionChange,
        updated_at,
        ensembl,
        methylation_horvath,
        lang,
        **kwargs
    ):
        self.id = id
        self.symbol = symbol
        self.name = name
        self.ncbiId = ncbi_id
        self.uniprot = uniprot

        origin = GeneDAO().get_origin_for_gene(phylum_id)
        if origin:
            self.origin = Origin(**origin)
        else:
            self.origin = None

        family_origin = GeneDAO().get_origin_for_gene(family_phylum_id)
        if family_origin:
            self.familyOrigin = Origin(**family_origin)
        else:
            self.familyOrigin = None

        self.homologueTaxon = GeneDAO().get_name_for_taxon(taxon_id)

        self.aliases = []
        if aliases:
            self.aliases = list(aliases.split())

        self.diseases = {}
        self.diseaseCategories = {}

        for disease_object in DiseaseDAO().get_from_gene(id):
            disease = DiseaseDAO().get_by_id(disease_object['disease_id'])
            self.diseases[disease_object['disease_id']] = DiseaseShort(**disease, lang=lang)
            if disease['icd_code_visible']:
                self.diseaseCategories[disease['icd_code_visible']] = DiseaseCategories(**disease, lang=lang)

        self.functionalClusters = []
        for cluster_object in FunctionalClusterDAO().get_from_gene(id):
            cluster = FunctionalClusterDAO().get_by_id(cluster_object['functional_cluster_id'])
            self.functionalClusters.append(FunctionalCluster(**cluster, lang=lang))

        self.expressionChange = expressionChange
        self.timestamp = updated_at
        self.ensembl = ensembl
        self.methylationCorrelation = methylation_horvath

        comment_сause = CommentCauseDAO().get_from_gene(id)
        self.commentCause = {}
        for comment_object in comment_сause:
            comment = CommentCauseDAO().get_by_id(comment_object['comment_cause_id'])
            self.commentCause[comment_object['comment_cause_id']] = CommentCause(**comment, lang=lang)


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
    researches: Researches = Field(title="Researches", description="Researches confirming the association of the gene with life expectancy and aging")
    expression: List[Expression] = Field(title="Gene expression in organs and tissues (NCBI)")
    proteinClasses: List[str] = Field(title="Protein classes", description="Protein classification by their function")
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
