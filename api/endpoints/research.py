from typing import List
from models.myresearch import MyIncreaseLifespanSearchInput, MyIncreaseLifespanSearchOutput

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
)

router = APIRouter()


@router.get('/research/lifespan-change/my', response_model=MyIncreaseLifespanSearchOutput)
async def increase_lifespan_search(
    input: MyIncreaseLifespanSearchInput = Depends(MyIncreaseLifespanSearchInput),
) -> List:
    return ResearchesDAO().my_increase_lifespan_search(input)


@router.get('/research/lifespan-change', response_model=IncreaseLifespanSearchOutput)
async def increase_lifespan_search(
    input: IncreaseLifespanSearchInput = Depends(IncreaseLifespanSearchInput),
) -> List:
    return ResearchesDAO().increase_lifespan_search(input)


@router.get('/research/age-related-changes', response_model=AgeRelatedChangeOfGeneResearchOutput)
async def age_related_changes_search(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().age_related_changes(input)


@router.get(
    '/research/gene-activity-change-impact', response_model=GeneActivityChangeImpactResearchedOutput
)
async def gene_activity_change_impact(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().gene_activity_change_impact(input)


@router.get('/research/gene-regulation', response_model=GeneRegulationResearchedOutput)
async def gene_regulation(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().gene_regulation(input)


@router.get(
    '/research/association-with-accelerated-aging',
    response_model=AssociationWithAcceleratedAgingResearchedOutput,
)
async def association_with_accelerated_aging(
    input: GeneSearchInput = Depends(GeneSearchInput),
) -> List:
    return ResearchesDAO().association_with_accelerated_aging(input)


@router.get(
    '/research/associations-with-lifespan', response_model=AssociationsWithLifespanResearchedOutput
)
async def associations_with_lifespan(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().associations_with_lifespan(input)


@router.get('/research/other-evidence', response_model=OtherEvidenceResearchedOutput)
async def other_evidence(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().other_evidence(input)
