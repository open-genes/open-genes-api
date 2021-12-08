from fastapi import APIRouter
from config import Language
from db.dao import CalorieExperimentDAO
from json import loads
from db.sql_raws.scripts import CALORIE_EXPERIMENT_QUERY
from db.request_handler import RequestHandler

router = APIRouter()


@router.get(
    '/calorie_experiment',
)
async def get_disease_list(lang: Language = Language.en, page: int = None, pageSize: int = None):
    sql_handler = RequestHandler(CALORIE_EXPERIMENT_QUERY)
    sql_handler.set_language(lang.value)
    sql_handler.set_pagination(page, pageSize)
    print(sql_handler.sql)
    return loads(CalorieExperimentDAO().get_list(request=sql_handler.sql)[0]['respJS'])