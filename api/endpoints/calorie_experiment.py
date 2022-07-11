from typing import List

from db.dao import CalorieExperimentDAO
from fastapi import APIRouter, Depends
from models.gene import CalorieExperimentInput, CalorieExperimentOutput

router = APIRouter()


@router.get('/diet', response_model=CalorieExperimentOutput)
async def increase_lifespan_search(
    input: CalorieExperimentInput = Depends(CalorieExperimentInput),
) -> List:
    return CalorieExperimentDAO().calorie_experiment_search(input)
