from json import loads
from typing import List

from config import Language
from db.dao import CalorieExperimentDAO
from db.request_handler import RequestHandler
from db.sql_raws.scripts import CALORIE_EXPERIMENT_QUERY
from fastapi import APIRouter
from presenters.output import DietOutput

router = APIRouter()


@router.get(
    '/diet',
    response_model=DietOutput
)
async def get_diet_list(lang: Language = Language.en, page: int = None, pageSize: int = None):
    sql_handler = RequestHandler(CALORIE_EXPERIMENT_QUERY)
    sql_handler.set_language(lang.value)
    sql_handler.set_pagination(page, pageSize)
    print(sql_handler.sql)
    return loads(CalorieExperimentDAO().get_list(request=sql_handler.sql)[0]['respJS'])