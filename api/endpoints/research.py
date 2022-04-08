from typing import List

from fastapi import APIRouter
from fastapi import Depends
from models.gene import GeneSearchInput

from db.dao import ResearchesDAO
from models.researches import IncreaseLifespanSearchInput, IncreaseLifespanSearchOutput, AgeRelatedChangeOfGeneResearchOutput

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
