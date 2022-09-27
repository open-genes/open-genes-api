from json import loads
from typing import List

from config import Cache, Language
from fastapi import APIRouter
from fastapi_cache.decorator import cache
from presenters.criteria import Criteria

from api.db.dao import CommentCauseDAO

router = APIRouter()


@router.get('/criteria', response_model=List[Criteria])
@cache(expire=int(Cache.expire), namespace=Cache.namespace)
async def get_criteria(lang: Language = Language.en):
    return loads(CommentCauseDAO().get_all(lang=lang.value)[0]['jsonobj'])
