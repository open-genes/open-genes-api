from json import loads
from typing import List

from config import Language
from presenters.criteria import Criteria
from fastapi import APIRouter
from api.db.dao import CriteriaDAO

router = APIRouter()


@router.get(
    '/criteria',
    response_model=List[Criteria]
)
async def get_diet_list(lang: Language = Language.en):
    return loads(CriteriaDAO().get_all()[0]['jsonobj'])