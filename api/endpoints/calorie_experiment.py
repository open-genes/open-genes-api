from typing import List
from api.db.dao import GeneSuggestionDAO

from db.dao import CalorieExperimentDAO
from fastapi import APIRouter, Depends
from models.gene import CalorieExperimentInput, CalorieExperimentOutput

router = APIRouter()


@router.get('/diet', response_model=CalorieExperimentOutput)
async def increase_lifespan_search(
    input: CalorieExperimentInput = Depends(CalorieExperimentInput),
) -> List:

    if input.bySuggestions is not None:
        sls = GeneSuggestionDAO().search(input.bySuggestions, suggestHidden=0)
        idls = []
        for item in sls['items']:
            idls.append(item['id'])
        suggfilter = ','.join(str(f) for f in idls) if idls else input.bySuggestions
        input.bySuggestions = None
        input.byGeneId = suggfilter
    return CalorieExperimentDAO().calorie_experiment_search(input)
