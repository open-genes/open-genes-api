from json import loads
from typing import List

from config import cache_if_enabled, Language
from fastapi import APIRouter
from presenters.criteria import Criteria

from api.db.dao import CommentCauseDAO

router = APIRouter()


@router.get('/criteria', response_model=List[Criteria])
@cache_if_enabled
async def get_criteria(lang: Language = Language.en):
    return loads(CommentCauseDAO().get_all(lang=lang.value)[0]['jsonobj'])
