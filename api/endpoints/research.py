from typing import List

from config import Cache
from db.dao import ResearchesDAO
from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
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


@router.get('/research/lifespan-change', response_model=IncreaseLifespanSearchOutput)
@cache(expire=int(Cache.expire), namespace=Cache.namespace)
async def increase_lifespan_search(
    input: IncreaseLifespanSearchInput = Depends(IncreaseLifespanSearchInput),
) -> List:
    return ResearchesDAO().increase_lifespan_search(input)


@router.get('/research/age-related-changes', response_model=AgeRelatedChangeOfGeneResearchOutput)
@cache(expire=int(Cache.expire), namespace=Cache.namespace)
async def age_related_changes_search(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().age_related_changes(input)


@router.get(
    '/research/gene-activity-change-impact', response_model=GeneActivityChangeImpactResearchedOutput
)
@cache(expire=int(Cache.expire), namespace=Cache.namespace)
async def gene_activity_change_impact(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().gene_activity_change_impact(input)


@router.get('/research/gene-regulation', response_model=GeneRegulationResearchedOutput)
@cache(expire=int(Cache.expire), namespace=Cache.namespace)
async def gene_regulation(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().gene_regulation(input)


@router.get(
    '/research/association-with-accelerated-aging',
    response_model=AssociationWithAcceleratedAgingResearchedOutput,
)
@cache(expire=int(Cache.expire), namespace=Cache.namespace)
async def association_with_accelerated_aging(
    input: GeneSearchInput = Depends(GeneSearchInput),
) -> List:
    return ResearchesDAO().association_with_accelerated_aging(input)


@router.get(
    '/research/associations-with-lifespan', response_model=AssociationsWithLifespanResearchedOutput
)
@cache(expire=int(Cache.expire), namespace=Cache.namespace)
async def associations_with_lifespan(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().associations_with_lifespan(input)


@router.get('/research/other-evidence', response_model=OtherEvidenceResearchedOutput)
@cache(expire=int(Cache.expire), namespace=Cache.namespace)
async def other_evidence(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:
    return ResearchesDAO().other_evidence(input)
