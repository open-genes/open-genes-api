from json import loads
from typing import List

from config import Cache, Language
from fastapi import APIRouter
from fastapi_cache.decorator import cache
from presenters.protein_class import ProteinClass

from api.db.dao import ProteinClassDAO

router = APIRouter()


@router.get('/protein-class', response_model=List[ProteinClass])
@cache(expire=int(Cache.expire), namespace=Cache.namespace)
async def get_protein_class(lang: Language = Language.en):
    return loads(ProteinClassDAO().get_all(lang=lang.value)[0]['jsonobj'])
