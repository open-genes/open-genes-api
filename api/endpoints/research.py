from typing import List

from db.dao import StudiesDAO
from fastapi import APIRouter, Depends
from models.gene import GeneSearchInput
from models.studies import (
    AgeRelatedChangeOfGeneResearchOutput,
    AssociationsWithLifespanResearchedOutput,
    AssociationWithAcceleratedAgingResearchedOutput,
    GeneActivityChangeImpactResearchedOutput,
    GeneRegulationResearchedOutput,
    IncreaseLifespanSearchInput,
    IncreaseLifespanSearchOutput,
    OtherEvidenceResearchedOutput,
)

router = APIRouter()


@router.get('/research/lifespan-change', response_model=IncreaseLifespanSearchOutput)
async def increase_lifespan_search(
    input: IncreaseLifespanSearchInput = Depends(IncreaseLifespanSearchInput),
) -> List:
    return StudiesDAO().increase_lifespan_search(input)


@router.get('/research/age-related-changes', response_model=AgeRelatedChangeOfGeneResearchOutput)
async def age_related_changes_search(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return StudiesDAO().age_related_changes(input)


@router.get(
    '/research/gene-activity-change-impact', response_model=GeneActivityChangeImpactResearchedOutput
)
async def gene_activity_change_impact(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return StudiesDAO().gene_activity_change_impact(input)


@router.get('/research/gene-regulation', response_model=GeneRegulationResearchedOutput)
async def gene_regulation(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return StudiesDAO().gene_regulation(input)


@router.get(
    '/research/association-with-accelerated-aging',
    response_model=AssociationWithAcceleratedAgingResearchedOutput,
)
async def association_with_accelerated_aging(
    input: GeneSearchInput = Depends(GeneSearchInput),
) -> List:
    return StudiesDAO().association_with_accelerated_aging(input)


@router.get(
    '/research/associations-with-lifespan', response_model=AssociationsWithLifespanResearchedOutput
)
async def associations_with_lifespan(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return StudiesDAO().associations_with_lifespan(input)


@router.get('/research/other-evidence', response_model=OtherEvidenceResearchedOutput)
async def other_evidence(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return StudiesDAO().other_evidence(input)
