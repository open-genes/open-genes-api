from typing import List

from fastapi import APIRouter
from fastapi import Depends
from models.gene import GeneSearchInput

from db.dao import ResearchesDAO
from models.researches import IncreaseLifespanSearchInput, IncreaseLifespanSearchOutput, \
    AgeRelatedChangeOfGeneResearchOutput, GeneActivityChangeImpactResearchedOutput, GeneRegulationResearchedOutput

router = APIRouter()


@router.get(
    '/research/lifespan-change',
    response_model=IncreaseLifespanSearchOutput
)
async def increase_lifespan_search(input: IncreaseLifespanSearchInput = Depends(IncreaseLifespanSearchInput)) -> List:
    return ResearchesDAO().increase_lifespan_search(input)


@router.get(
    '/research/age-related-changes',
    response_model=AgeRelatedChangeOfGeneResearchOutput
)
async def age_related_changes_search(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().age_related_changes(input)


@router.get(
    '/research/gene-activity-change-impact',
    response_model=GeneActivityChangeImpactResearchedOutput
)
async def gene_activity_change_impact(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().gene_activity_change_impact(input)

@router.get(
    '/research/gene-regulation',
    response_model=GeneRegulationResearchedOutput
)
async def gene_regulation(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().gene_regulation(input)
