from typing import List

from config import Cache
from db.dao import CalorieExperimentDAO
from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from models.gene import CalorieExperimentInput, CalorieExperimentOutput

router = APIRouter()


@router.get('/diet', response_model=CalorieExperimentOutput)
@cache(expire=int(Cache.expire), namespace=Cache.namespace)
async def increase_lifespan_search(
    input: CalorieExperimentInput = Depends(CalorieExperimentInput),
) -> List:
    return CalorieExperimentDAO().calorie_experiment_search(input)
