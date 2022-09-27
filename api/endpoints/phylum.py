from json import loads
from typing import List

from config import Cache
from fastapi import APIRouter
from fastapi_cache.decorator import cache
from presenters.phylum import PhylumOutput

from api.db.dao import PhylumDAO

router = APIRouter()


@router.get('/phylum', response_model=List[PhylumOutput])
@cache(expire=int(Cache.expire), namespace=Cache.namespace)
async def get_phylum():
    return loads(PhylumDAO().get_all()[0]['jsonobj'])
