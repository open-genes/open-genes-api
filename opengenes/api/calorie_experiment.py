from json import loads
from typing import List

from fastapi import APIRouter
from opengenes.config import Language
from opengenes.db.dao import CalorieExperimentDAO
from opengenes.presenters.calorie_experiment import CalorieRestrictionExperiment

router = APIRouter()


@router.get(
    '/calorie_experiment',
)
async def get_disease_list(lang: Language):
    return CalorieExperimentDAO().get_list()
