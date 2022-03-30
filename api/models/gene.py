from pydantic import BaseModel
from models import *
from models.calorie_experiment import CalorieRestrictionExperiment

class Phylum(BaseModel):
    id:int
    phylum:str
    age:str
    order:int

class DiseaseCategory(BaseModel):
    id:int
    icdCode:str
    icdCategoryName:str

class Disease(BaseModel):
    id:int
    icdCode:str|None
    name:str|None
    icdName:str|None

class CommentCause(BaseModel):
    id:int
    name:str

class ProteinClass(BaseModel):
    id:int
    name:str

class AgingMechanism(BaseModel):
    id:int
    name:str

class FunctionalCluster(BaseModel):
    id:int
    name:str

from models.researches import *

class Gene(BaseModel):
    id: int
    homologueTaxon:str|None
    symbol:str|None
    chromosome:str|None
    name:str|None
    ncbiId:int|None
    uniprot:str|None
    timestamp:ogmodel(Timestamp,_select={'created':'gene.created_at','changed':'gene.updated_at'})
    ensembl:str|None
    methylationCorrelation:str|None
    aliases:List[str]|None
    expressionChange:int

    origin:None|ogmodel(Phylum,
        _select=
        {
            'id':"phylum.id",
            'phylum':"phylum.name_phylo",
            'age':"phylum.name_mya",
            'order':"phylum.order",
        },
        _join='LEFT JOIN phylum ON gene.phylum_id = phylum.id'
    )
    familyOrigin:None|ogmodel(Phylum,
        _select=
        {
            'id':"family_phylum.id",
            'phylum':"family_phylum.name_phylo",
            'age':"family_phylum.name_mya",
            'order':"family_phylum.order",
        },
        _join='LEFT JOIN phylum family_phylum ON gene.family_phylum_id = family_phylum.id'
    )

    diseaseCategories:List[ogmodel(DiseaseCategory,
        _select=
        {
            'id':'disease_category.id',
            'icdCode':"disease_category.icd_code",
            'icdCategoryName':"COALESCE(disease_category.icd_name_@LANG@,disease.icd_name_@LANG@)",
        },
        _from="""
from gene join gene_to_disease on gene_to_disease.gene_id=gene.id
join open_genes.disease on disease.id=gene_to_disease.disease_id and not exists (select 1 from open_genes.disease d where disease.icd_code_visible=d.icd_code_visible and disease.id>d.id)
join open_genes.disease disease_category on disease_category.icd_code=disease.icd_code_visible
"""
    )]

    diseases:List[ogmodel(Disease,
        _select=
        {
            'id':"disease.id",
            'icdCode':"disease.icd_code",
            'name':"COALESCE(disease.name_@LANG@,disease.name_@LANG@)",
            'icdName':"COALESCE(disease.icd_name_@LANG@,disease.icd_name_@LANG@)",
        },
        _from="from gene join gene_to_disease on gene_to_disease.gene_id=gene.id join disease on disease.id=gene_to_disease.disease_id",
    )]

    commentCause:List[ogmodel(CommentCause,
        _select=
        {
            'id':"comment_cause.id",
            'name':"COALESCE(comment_cause.name_@LANG@,comment_cause.name_en)",
        },
        _from="from gene join gene_to_comment_cause on gene_to_comment_cause.gene_id=gene.id join comment_cause on comment_cause.id=gene_to_comment_cause.comment_cause_id",
    )]

    proteinClasses:List[ogmodel(ProteinClass,
        _select=
        {
            'id':"protein_class.id",
            'name':"COALESCE(protein_class.name_en,protein_class.name_en)",
        },
        _from="from gene join gene_to_protein_class on gene_to_protein_class.gene_id=gene.id join  protein_class on protein_class.id=gene_to_protein_class.protein_class_id",
    )]

    agingMechanisms:List[ogmodel(AgingMechanism,
        _select=
        {
            'id':'aging_mechanism.id',
            'name':'coalesce(aging_mechanism.name_@LANG@,aging_mechanism.name_en)',
        },
        _from="""
FROM gene
LEFT JOIN `gene_to_ontology` ON gene_to_ontology.gene_id = gene.id
LEFT JOIN `gene_ontology_to_aging_mechanism_visible` ON gene_to_ontology.gene_ontology_id = gene_ontology_to_aging_mechanism_visible.gene_ontology_id
INNER JOIN `aging_mechanism` ON gene_ontology_to_aging_mechanism_visible.aging_mechanism_id = aging_mechanism.id AND aging_mechanism.name_en != '' """,
    )]

    functionalClusters:List[ogmodel(FunctionalCluster,
        _select=
        {
            'id':'functional_cluster.id',
            'name':'coalesce(functional_cluster.name_@LANG@,functional_cluster.name_en)',
        },
        _from="""
FROM gene
LEFT JOIN `gene_to_functional_cluster` ON gene_to_functional_cluster.gene_id = gene.id
join functional_cluster on functional_cluster.id=gene_to_functional_cluster.functional_cluster_id
"""
    )]

    researches:None|Researches

    _name='gene'
    _select= {
        'id':'gene.id',
        'homologueTaxon':"COALESCE(taxon.name_@LANG@,taxon.name_en)",
        'symbol':"gene.symbol",
        'chromosome':"gene.chromosome",
        'name':"gene.name",
        'ncbiId':"gene.ncbi_id",
        'uniprot':"gene.uniprot",
        'ensembl':"gene.ensembl",
        'methylationCorrelation':"gene.methylation_horvath",
        'aliases':"gene.aliases",
        'expressionChange':'gene.expressionChange',
    }

    _from="""
FROM gene
LEFT JOIN taxon ON gene.taxon_id = taxon.id
@JOINS@
@FILTERING@
order by @ORDERING@ gene.id
@PAGING@

"""

class GeneSearched(PaginatedOutput):
    items:List[Gene]

class GeneSearchInput(PaginationInput, LanguageInput, SortInput):
    byDiseases: str = None
    byDiseaseCategories: str = None
    byAgeRelatedProcess: str = None
    byExpressionChange: str = None
    bySelectionCriteria: str = None
    byAgingMechanism: str = None
    byProteinClass: str = None
    bySpecies: str = None
    byGeneId: str = None
    byGeneSymbol: str = None
    bySuggestions: str = None
    byChromosomeNum: str = None
    sortBy: Literal['criteriaQuantity','familyPhylum']|None = None
    researches: str=None
    isHidden:str = 1
    _filters = {
        'isHidden':[lambda value: 'gene.isHidden!=1',lambda value: []],
        'byGeneId':[lambda value: 'gene.id in ('+','.join(['%s' for v in value.split(',')])+')',lambda value: value.split(',')],
        'byChromosomeNum':[lambda value: 'gene.chromosome in ('+','.join(['%s' for v in value.split(',')])+')',lambda value: value.split(',')],
        'byGeneSymbol':[lambda value: 'gene.symbol in ('+','.join(['%s' for v in value.split(',')])+')',lambda value: value.split(',')],
        'byDiseases': [lambda value:'(select count(*) from gene_to_disease where gene_to_disease.gene_id=gene.id and disease_id in ('+','.join(['%s' for v in value.split(',')])+'))=%s',lambda value:value.split(',')+[len(value.split(','))]],
        'byDiseaseCategories': [lambda value:'(select count(*) from gene_to_disease g join disease d on g.disease_id=d.id join disease c on c.icd_code=d.icd_code_visible where g.gene_id=gene.id and c.id in ('+','.join(['%s' for v in value.split(',')])+'))=%s',lambda value:value.split(',')+[len(value.split(','))]],
        'byAgeRelatedProcess': [lambda value:'(select count(*) from gene_to_functional_cluster where gene_id=gene.id and functional_cluster_id in ('+','.join(['%s' for v in value.split(',')])+'))=%s',lambda value:value.split(',')+[len(value.split(','))]],
        'byExpressionChange': [lambda value:'gene.expressionChange in ('+','.join(['%s' for v in value.split(',')])+')',lambda value:value.split(',')],
        'bySelectionCriteria': [lambda value:'(select count(*) from gene_to_comment_cause where gene_id=gene.id and comment_cause_id in ('+','.join(['%s' for v in value.split(',')])+'))=%s',lambda value:value.split(',')+[len(value.split(','))]],
        'byAgingMechanism': [lambda value:'(select count(distinct aging_mechanism_id) from gene_to_ontology o join gene_ontology_to_aging_mechanism_visible a on a.gene_ontology_id=o.gene_ontology_id where o.gene_id=gene.id and aging_mechanism_id in ('+','.join(['%s' for v in value.split(',')])+'))=%s',lambda value:value.split(',')+[len(value.split(','))]],
        'byProteinClass': [lambda value:'(select count(*) from gene_to_protein_class where gene_id=gene.id and protein_class_id in ('+','.join(['%s' for v in value.split(',')])+'))=%s',lambda value:value.split(',')+[len(value.split(','))]],
        'bySpecies': [lambda value:'(select count(distinct model_organism_id) from lifespan_experiment where lifespan_experiment.gene_id=gene.id and model_organism_id in ('+','.join(['%s' for v in value.split(',')])+'))=%s',lambda value:value.split(',')+[len(value.split(','))]],

    }
    _sorts = {
        'criteriaQuantity':'(select count(*) from gene_to_comment_cause where gene_id=gene.id)',
        'familyPhylum':'(select `order` from phylum where phylum.id=family_phylum_id)',
    }


class CalorieExperiment(BaseModel):
    id: int
    name: str | None
    symbol:str|None
    ncbiId:int|None
    uniprot:str|None
    ensembl:str|None
    calorieRestrictionExperiments: List[CalorieRestrictionExperiment]
    _name='gene'
    _select= {
        'id':'gene.id',
        'symbol':"gene.symbol",
        'name':"gene.name",
        'ncbiId':"gene.ncbi_id",
        'uniprot':"gene.uniprot",
        'ensembl':"gene.ensembl",
    }


    _from="""
FROM gene
RIGHT JOIN calorie_restriction_experiment ON calorie_restriction_experiment.gene_id = gene.id
@JOINS@
@FILTERING@
order by @ORDERING@ gene.id
@PAGING@
"""


class CalorieExperimentOutput(PaginatedOutput):
    items: List[CalorieExperiment]


class CalorieExperimentInput(PaginationInput, LanguageInput):
    _filters = {}
    _sorts = {}