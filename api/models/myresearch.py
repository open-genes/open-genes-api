from models import *
from pydantic import BaseModel


class GeneralLifespanExperiment(BaseModel):
    id: int
    modelOrganism: str | None
    modelOrganismId: int | None


class MyIncreaseLifespan(GeneralLifespanExperiment):
    _select = {
        'id': 'general_lifespan_experiment.id',
        'modelOrganism': 'model_organism.name_@LANG@',
        'modelOrganismId': 'model_organism.id',

    }
#     _from = """
# from gene
# join lifespan_experiment on lifespan_experiment.gene_id=gene.id
# left join general_lifespan_experiment on general_lifespan_experiment.id = lifespan_experiment.general_lifespan_experiment_id
# join model_organism on general_lifespan_experiment_model_organism.id = general_lifespan_experiment.model_organism_id
# """


class Researches(BaseModel):
    increaseLifespan: List[MyIncreaseLifespan]


class MyIncreaseLifespanSearchInput(PaginationInput, LanguageInput, SortInput):
    bySpecies: str = 3
    isHidden: str = 1
    _filters = {
        'byAgingMechanism': [
            lambda value: '(select count(distinct aging_mechanism_id) from gene_to_ontology o join gene_ontology_to_aging_mechanism_visible a on a.gene_ontology_id=o.gene_ontology_id where o.gene_id=gene.id and aging_mechanism_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        
        'bySpecies': [
            lambda value: '(select count(distinct model_organism_id) from lifespan_experiment where lifespan_experiment.gene_id=gene.id and model_organism_id in ('
            # lambda value: '(select count(distinct model_organism_id) from lifespan_experiment where lifespan_experiment.gene_id=gene.id and model_organism_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ]
    }


class MyIncreaseLifespanSearched(MyIncreaseLifespan):
    geneId: int
    _select = MyIncreaseLifespan._select | {
        'geneId': 'gene.id',
    }
    _name = 'increaseLifespan'

    _from = """
from general_lifespan_experiment
join lifespan_experiment on lifespan_experiment.general_lifespan_experiment_id=general_lifespan_experiment.id
join gene on gene.id = lifespan_experiment.gene_id
join model_organism on model_organism.id = general_lifespan_experiment.model_organism_id
@FILTERING@
@PAGING@
"""
    _order_by = "general_lifespan_experiment.id"


class MyIncreaseLifespanSearchOutput(PaginatedOutput):
    items: List[MyIncreaseLifespanSearched]
