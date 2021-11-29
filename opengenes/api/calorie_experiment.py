from typing import List

from fastapi import APIRouter

from opengenes.config import Language
from opengenes.db.dao import DiseaseDAO
from opengenes.presenters.calorie_experiment import CalorieRestrictionExperiment

router = APIRouter()


@router.get(
    '/calorie_experiment',
    response_model=List[CalorieRestrictionExperiment],
)
async def get_disease_list(lang: Language):
    return DiseaseDAO().get()


