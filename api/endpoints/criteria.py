from json import loads
from typing import List

from config import Language
from presenters.criteria import Criteria
from fastapi import APIRouter
from api.db.dao import CommentCauseDAO

router = APIRouter()


@router.get(
    '/criteria',
    response_model=List[Criteria]
)
async def get_criteria(lang: Language = Language.en):
    return loads(CommentCauseDAO().get_all(lang=lang.value)[0]['jsonobj'])