from typing import List

from config import cache_if_enabled
from db.dao import ResearchesDAO
from fastapi import APIRouter, Depends
from models.gene import GeneSearchInput
from models.researches import (
    AgeRelatedChangeOfGeneResearchOutput,
    AssociationsWithLifespanResearchedOutput,
    AssociationWithAcceleratedAgingResearchedOutput,
    GeneActivityChangeImpactResearchedOutput,
    GeneRegulationResearchedOutput,
    IncreaseLifespanSearchInput,
    IncreaseLifespanSearchOutput,
    OtherEvidenceResearchedOutput,
    StudySearchByExperimentInput
)

router = APIRouter()



@router.get('/lifespan-change', response_model=IncreaseLifespanSearchOutput)
@cache_if_enabled

async def increase_lifespan_search(
    input: IncreaseLifespanSearchInput = Depends(IncreaseLifespanSearchInput),
) -> List:
    return ResearchesDAO().increase_lifespan_search(input)

@router.get('/age-related-changes', response_model=AgeRelatedChangeOfGeneResearchOutput)
@cache_if_enabled

async def age_related_changes_search(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().age_related_changes(input)


@router.get(
    '/gene-activity-change-impact', response_model=GeneActivityChangeImpactResearchedOutput
)
@cache_if_enabled
async def gene_activity_change_impact(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().gene_activity_change_impact(input)



@router.get('/gene-regulation', response_model=GeneRegulationResearchedOutput)
@cache_if_enabled

async def gene_regulation(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().gene_regulation(input)


@router.get(
    '/association-with-accelerated-aging',
    response_model=AssociationWithAcceleratedAgingResearchedOutput,
)
@cache_if_enabled
async def association_with_accelerated_aging(
    input: GeneSearchInput = Depends(GeneSearchInput),
) -> List:
    return ResearchesDAO().association_with_accelerated_aging(input)


@router.get(
    '/associations-with-lifespan', response_model=AssociationsWithLifespanResearchedOutput
)
@cache_if_enabled
async def associations_with_lifespan(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().associations_with_lifespan(input)


@router.get('/other-evidence', response_model=OtherEvidenceResearchedOutput)
@cache_if_enabled

async def other_evidence(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().other_evidence(input)


@router.get('/lifespan-change/{id}', response_model=IncreaseLifespanSearchOutput)
async def increase_lifespan_search_by_experiment(
    input: StudySearchByExperimentInput = Depends(StudySearchByExperimentInput),
) -> List:
    "Filtered by general_lifespan_experiment.id"
    input._filters['id'] = input._filters['general_lifespan_experiment_id']
    return ResearchesDAO().increase_lifespan_search(input)


@router.get('/age-related-changes/{id}', response_model=AgeRelatedChangeOfGeneResearchOutput)
async def age_related_changes_search_by_experiment(
    input: StudySearchByExperimentInput = Depends(StudySearchByExperimentInput)
    ) -> List:
    "Filtered by age_related_change.id"
    input._filters['id'] = input._filters['age_related_change_id']
    return ResearchesDAO().age_related_changes(input)


@router.get(
    '/gene-activity-change-impact/{id}', response_model=GeneActivityChangeImpactResearchedOutput
)
async def gene_activity_change_impact_by_experiment(
    input: StudySearchByExperimentInput = Depends(StudySearchByExperimentInput)
    ) -> List:
    "Filtered by gene_intervention_to_vital_process.id"
    input._filters['id'] = input._filters['gene_intervention_to_vital_process_id']
    return ResearchesDAO().gene_activity_change_impact(input)


@router.get('/gene-regulation/{id}', response_model=GeneRegulationResearchedOutput)
async def gene_regulation(
    input: StudySearchByExperimentInput = Depends(StudySearchByExperimentInput)
    ) -> List:
    "Filtered by protein_activity.id"
    input._filters['id'] = input._filters['protein_activity_id']
    return ResearchesDAO().gene_regulation(input)


@router.get(
    '/association-with-accelerated-aging/{id}',
    response_model=AssociationWithAcceleratedAgingResearchedOutput,
)
async def association_with_accelerated_aging(
    input: StudySearchByExperimentInput = Depends(StudySearchByExperimentInput)
) -> List:
    "Filtered by progeria_syndrome.id"
    input._filters['id'] = input._filters['progeria_syndrome_id']
    return ResearchesDAO().association_with_accelerated_aging(input)


@router.get(
    '/associations-with-lifespan/{id}', response_model=AssociationsWithLifespanResearchedOutput
)
async def associations_with_lifespan(
    input: StudySearchByExperimentInput = Depends(StudySearchByExperimentInput)
    ) -> List:
    "Filtered by longevity_effect.id"
    input._filters['id'] = input._filters['longevity_effect_id']
    return ResearchesDAO().associations_with_lifespan(input)


@router.get('/other-evidence/{id}', response_model=OtherEvidenceResearchedOutput)
async def other_evidence(
    input: StudySearchByExperimentInput = Depends(StudySearchByExperimentInput)
    ) -> List:
    "Filtered by longevity_effect.id"
    input._filters['id'] = input._filters['gene_to_additional_evidence_id']
    return ResearchesDAO().other_evidence(input)
