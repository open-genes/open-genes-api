from typing import Any, Optional, Type, Union
from models import *
from models.calorie_experiment import CalorieRestrictionExperiment
from models.location import *
from models.researches import *
from pydantic import BaseModel


class Phylum(BaseModel):
    id: int
    phylum: str
    age: str
    order: int


class DiseaseCategory(BaseModel):
    id: int
    icdCode: str
    icdCategoryName: str | None


class Disease(BaseModel):
    id: int
    icdCode: str | None
    name: str | None
    icdName: str | None


class CommentCause(BaseModel):
    id: int
    name: str


class ProteinClass(BaseModel):
    id: int
    name: str


class AgingMechanism(BaseModel):
    id: Optional[int] = None
    name: str
    uuid: Optional[str] = None


class FunctionalCluster(BaseModel):
    id: int
    name: str


class ConfidenceLevel(BaseModel):
    id: int
    name: str


class GeneCommon(BaseModel):
    id: int
    homologueTaxon: str | None
    symbol: str | None
    chromosome: str | None
    name: str | None
    ncbiId: int | None
    uniprot: str | None
    timestamp: ogmodel(
        Timestamp, _select={'created': 'gene.created_at', 'changed': 'gene.updated_at'}
    )
    ensembl: str | None
    methylationCorrelation: str | None
    aliases: List[str] | None
    expressionChange: int
    confidenceLevel: None | ogmodel(
        ConfidenceLevel,
        _select={
            'id': "confidence_level.id",
            'name': "COALESCE(confidence_level.name_@LANG@,confidence_level.name_en)",
        },
        _join='LEFT JOIN confidence_level ON gene.confidence_level_id = confidence_level.id',
    )

    origin: None | ogmodel(
        Phylum,
        _select={
            'id': "phylum.id",
            'phylum': "phylum.name_phylo",
            'age': "phylum.name_mya",
            'order': "phylum.order",
        },
        _join='LEFT JOIN phylum ON gene.phylum_id = phylum.id',
    )
    familyOrigin: None | ogmodel(
        Phylum,
        _select={
            'id': "family_phylum.id",
            'phylum': "family_phylum.name_phylo",
            'age': "family_phylum.name_mya",
            'order': "family_phylum.order",
        },
        _join='LEFT JOIN phylum family_phylum ON gene.family_phylum_id = family_phylum.id',
    )

    diseaseCategories: List[
        ogmodel(
            DiseaseCategory,
            _select={
                'id': 'disease_category.id',
                'icdCode': "disease_category.icd_code",
                'icdCategoryName': "COALESCE(disease_category.icd_name_@LANG@,disease.icd_name_@LANG@)",
            },
            _from="""
from gene join gene_to_disease on gene_to_disease.gene_id=gene.id
join disease on disease.id=gene_to_disease.disease_id and not exists (select 1 from disease d where disease.icd_code_visible=d.icd_code_visible and disease.id>d.id)
join disease disease_category on disease_category.icd_code=disease.icd_code_visible
""",
        )
    ]

    diseases: List[
        ogmodel(
            Disease,
            _select={
                'id': "disease.id",
                'icdCode': "disease.icd_code",
                'name': "COALESCE(disease.name_@LANG@,disease.name_@LANG@)",
                'icdName': "COALESCE(disease.icd_name_@LANG@,disease.icd_name_@LANG@)",
            },
            _from="from gene join gene_to_disease on gene_to_disease.gene_id=gene.id join disease on disease.id=gene_to_disease.disease_id",
        )
    ]

    commentCause: List[
        ogmodel(
            CommentCause,
            _select={
                'id': "comment_cause.id",
                'name': "COALESCE(comment_cause.name_@LANG@,comment_cause.name_en)",
            },
            _from="from gene join gene_to_comment_cause on gene_to_comment_cause.gene_id=gene.id join comment_cause on comment_cause.id=gene_to_comment_cause.comment_cause_id",
        )
    ]

    proteinClasses: List[
        ogmodel(
            ProteinClass,
            _select={
                'id': "protein_class.id",
                'name': "COALESCE(protein_class.name_@LANG@, protein_class.name_en)",
            },
            _from="from gene join gene_to_protein_class on gene_to_protein_class.gene_id=gene.id join  protein_class on protein_class.id=gene_to_protein_class.protein_class_id",
        )
    ]

    agingMechanisms: List[
        ogmodel(
            AgingMechanism,
            _select={
                'id': 'aging_mechanism.id',
                'name': 'coalesce(aging_mechanism.name_@LANG@, aging_mechanism.name_ru)',
                'uuid': 'NULL'
            },
            _from="""
FROM gene 
LEFT JOIN gene_to_ontology ON gene_to_ontology.gene_id = gene.id
LEFT JOIN gene_ontology_relation ON gene_to_ontology.gene_ontology_id = gene_ontology_parent_id
LEFT JOIN gene_ontology_to_aging_mechanism_visible ON gene_to_ontology.gene_ontology_id = gene_ontology_to_aging_mechanism_visible.gene_ontology_id
INNER JOIN aging_mechanism ON gene_ontology_to_aging_mechanism_visible.aging_mechanism_id = aging_mechanism.id AND aging_mechanism.name_en != ''
UNION 
SELECT 'dummy_constant', NULL, COALESCE(aging_mechanism.name_@LANG@, aging_mechanism.name_en), aging_mechanism_to_gene.uuid
FROM aging_mechanism
JOIN aging_mechanism_to_gene ON aging_mechanism.id = aging_mechanism_to_gene.aging_mechanism_id
JOIN gene ON aging_mechanism_to_gene.gene_id = gene.id
""",
        )
    ]

    functionalClusters: List[
        ogmodel(
            FunctionalCluster,
            _select={
                'id': 'functional_cluster.id',
                'name': 'coalesce(functional_cluster.name_@LANG@,functional_cluster.name_en)',
            },
            _from="""
FROM gene
LEFT JOIN `gene_to_functional_cluster` ON gene_to_functional_cluster.gene_id = gene.id
join functional_cluster on functional_cluster.id=gene_to_functional_cluster.functional_cluster_id
""",
        )
    ]

    researches: None | Researches

    location: None | Location

    _name = 'gene'
    _select = {
        'id': 'gene.id',
        'homologueTaxon': "COALESCE(taxon.name_@LANG@,taxon.name_en)",
        'symbol': "gene.symbol",
        'chromosome': "gene.chromosome",
        'name': "gene.name",
        'ncbiId': "gene.ncbi_id",
        'uniprot': "gene.uniprot",
        'ensembl': "gene.ensembl",
        'methylationCorrelation': "gene.methylation_horvath",
        'aliases': "gene.aliases",
        'expressionChange': 'gene.expressionChange',
    }


class GeneSearched(GeneCommon):
    _from = """
FROM gene
LEFT JOIN taxon ON gene.taxon_id = taxon.id
@JOINS@
@FILTERING@
@PAGING@
"""
    _order_by = "gene.id"


class GeneSearchOutput(PaginatedOutput):
    items: List[GeneSearched]
    _from = "from (select coalesce((select row_count from @PRIMARY_TABLE@ limit 1),0) as objTotal, (select count(*) from @DBNAME@.gene where isHidden<>1) as total, %s as page, coalesce(nullif(%s,0),(select row_count from @PRIMARY_TABLE@ limit 1)) as pageSize, %s as pagesTotal) s "


class GeneSearchInput(PaginationInput, LanguageInput, SortInput):
    byDiseases: str = None
    byDiseaseCategories: str = None
    byAgeRelatedProcess: str = None
    byExpressionChange: str = None
    bySelectionCriteria: str = None
    byAgingMechanism: str = None
    byAgingMechanismUUID: str = None
    byProteinClass: str = None
    bySpecies: str = None
    byOrigin: str = None
    byFamilyOrigin: str = None
    byConservativeIn: str = None
    byGeneId: str = None
    byGeneSymbol: str = None
    bySuggestions: str = None
    byChromosomeNum: str = None
    sortBy: Literal['criteriaQuantity', 'familyPhylum', 'byConfidenceLevel'] | None = None
    researches: str = None
    isHidden: str = 1
    confidenceLevel: str | None = None
    _filters = {
        'isHidden': [lambda value: 'gene.isHidden!=1', lambda value: []],
        'byGeneId': [
            lambda value: 'gene.id in (' + ','.join(['%s' for v in value.split(',')]) + ')',
            lambda value: value.split(','),
        ],
        'byChromosomeNum': [
            lambda value: 'gene.chromosome in (' + ','.join(['%s' for v in value.split(',')]) + ')',
            lambda value: value.split(','),
        ],
        'byGeneSymbol': [
            lambda value: 'gene.symbol in (' + ','.join(['%s' for v in value.split(',')]) + ')',
            lambda value: value.split(','),
        ],
        'byDiseases': [
            lambda value: '(select count(*) from gene_to_disease where gene_to_disease.gene_id=gene.id and disease_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byDiseaseCategories': [
            lambda value: '(select count(*) from gene_to_disease g join disease d on g.disease_id=d.id join disease c on c.icd_code=d.icd_code_visible where g.gene_id=gene.id and c.id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byAgeRelatedProcess': [
            lambda value: '(select count(*) from gene_to_functional_cluster where gene_id=gene.id and functional_cluster_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byExpressionChange': [
            lambda value: 'gene.expressionChange in ('
            + ','.join(['%s' for v in value.split(',')])
            + ')',
            lambda value: value.split(','),
        ],
        'bySelectionCriteria': [
            lambda value: '(select count(*) from gene_to_comment_cause where gene_id=gene.id and comment_cause_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byAgingMechanism': [
            lambda value: '''
            (SELECT COUNT(distinct aging_mechanism_id)
            FROM gene_to_ontology AS o
            JOIN gene_ontology_to_aging_mechanism_visible AS a
            ON a.gene_ontology_id=o.gene_ontology_id
            WHERE o.gene_id=gene.id AND aging_mechanism_id in (
            '''
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byAgingMechanismUUID': [
            lambda value: '''
            (SELECT COUNT(distinct uuid)
            FROM aging_mechanism_to_gene AS amtg
            WHERE amtg.gene_id=gene.id AND uuid in (
            '''
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byProteinClass': [
            lambda value: '(select count(*) from gene_to_protein_class where gene_id=gene.id and protein_class_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'bySpecies': [
            lambda value: '(select count(distinct model_organism_id) from lifespan_experiment where lifespan_experiment.gene_id=gene.id and model_organism_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byOrigin': [
            lambda value: '(select count(*) from phylum where gene.phylum_id=phylum.id and phylum.name_phylo in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byFamilyOrigin': [
            lambda value: '(select count(*) from phylum where gene.phylum_id=family_phylum.id and phylum.id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byConservativeIn': [
            lambda value: '(select count(*) from taxon where gene.taxon_id=taxon.id and taxon.id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'confidenceLevel': [
            lambda value: 'gene.confidence_level_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + ')',
            lambda value: value.split(','),
        ],
    }
    _sorts = {
        'criteriaQuantity': '(select count(*) from gene_to_comment_cause where gene_id=gene.id)',
        'familyPhylum': '(select `order` from phylum where phylum.id=family_phylum_id)',
        'byConfidenceLevel': '(select id from confidence_level where confidence_level.id=gene.confidence_level_id)',
    }


class GeneSingleInput(LanguageInput):
    byGeneId: int | None
    bySymbol: str | None
    researches: str = '1'
    _filters = {
        'byGeneId': [lambda value: 'gene.id = %s', lambda value: [value]],
        'bySymbol': [lambda value: 'gene.symbol = %s', lambda value: [value]],
    }
    _sorts = {}


class ExpressionInSample(BaseModel):
    name: str | None
    exp_rpkm: float
    _select = {
        'name': 'sample.name_@LANG@',
        'exp_rpkm': 'expression_value',
    }
    _from = """
from gene
join gene_expression_in_sample  on gene_expression_in_sample.gene_id=gene.id
join sample on gene_expression_in_sample.sample_id=sample.id
order by 2 desc
"""


class OrthologSpecies(BaseModel):
    latinName: str
    commonName: None | str
    _select = {
        'latinName': 'model_organism.name_lat',
        'commonName': 'model_organism.name_@LANG@',
    }


class Ortholog(BaseModel):
    id: int
    symbol: str
    species: OrthologSpecies
    externalBaseName: str | None
    externalBaseId: str | None

    _select = {
        'id': 'ortholog.id',
        'symbol': 'ortholog.symbol',
        'externalBaseName': 'ortholog.external_base_name',
        'externalBaseId': 'ortholog.external_base_id',
    }
    _from = """
from gene
join gene_to_ortholog on gene_to_ortholog.gene_id = gene.id
join ortholog on gene_to_ortholog.ortholog_id = ortholog.id
left join model_organism on ortholog.model_organism_id = model_organism.id
"""


class GOTerm(BaseModel):
    id: int
    GOId: str
    term: str
    _select = {
        'id': 'gene_ontology.id',
        'GOId': 'gene_ontology.ontology_identifier',
        'term': 'COALESCE(gene_ontology.name_@LANG@,gene_ontology.name_en)',
    }
    _from = """
from gene
join gene_to_ontology on gene_to_ontology.gene_id=gene.id
join gene_ontology on gene_ontology.id=gene_to_ontology.gene_ontology_id
"""


class GOTermB(GOTerm):
    _from = GOTerm._from + "where gene_ontology.category='biological_process'\n"


class GOTermM(GOTerm):
    _from = GOTerm._from + "where gene_ontology.category='molecular_activity'\n"


class GOTermC(GOTerm):
    _from = GOTerm._from + "where gene_ontology.category='cellular_component'\n"


class GOTerms(BaseModel):
    biological_process: List[GOTermB]
    molecular_activity: List[GOTermM]
    cellular_component: List[GOTermC]


class Source(str):
    _select = {'_value': 'source.name'}
    _from = """
from gene
join gene_to_source on gene_to_source.gene_id=gene.id
join source on source.id=gene_to_source.source_id
"""


class GeneSingle(GeneCommon):
    commentEvolution: str | None
    proteinDescriptionUniProt: str | None
    descriptionNCBI: str | None
    proteinDescriptionOpenGenes: str | None
    expression: List[ExpressionInSample]
    terms: GOTerms
    ortholog: List[Ortholog]
    humanProteinAtlas: dict
    source: List[Source] | None
    _select = GeneCommon._select | {
        'commentEvolution': 'gene.commentEvolution@LANG2@',
        'proteinDescriptionUniProt': 'gene.uniprot_summary_@LANG@',
        'descriptionNCBI': 'gene.ncbi_summary_@LANG@',
        'proteinDescriptionOpenGenes': 'gene.og_summary_@LANG@',
        'humanProteinAtlas': 'gene.human_protein_atlas',
    }
    _from = """
FROM gene
LEFT JOIN taxon ON gene.taxon_id = taxon.id
@JOINS@
@FILTERING@
"""


class CalorieExperiment(BaseModel):
    id: int
    name: str | None
    symbol: str | None
    ncbiId: int | None
    uniprot: str | None
    ensembl: str | None
    isHidden: bool | None
    calorieRestrictionExperiments: List[CalorieRestrictionExperiment]
    _name = 'gene'
    _select = {
        'id': 'gene.id',
        'symbol': "gene.symbol",
        'name': "gene.name",
        'ncbiId': "gene.ncbi_id",
        'uniprot': "gene.uniprot",
        'ensembl': "gene.ensembl",
        'isHidden': "gene.isHidden",
    }

    _from = """
FROM gene
RIGHT JOIN calorie_restriction_experiment ON calorie_restriction_experiment.gene_id = gene.id
@JOINS@
@FILTERING@
@PAGING@
"""
    _order_by = "gene.id"


class CalorieExperimentOutput(PaginatedOutput):
    items: List[CalorieExperiment]


class CalorieExperimentInput(PaginationInput, LanguageInput):
    _filters = {}
    _sorts = {}
