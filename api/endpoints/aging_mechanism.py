from json import loads
from typing import List

from config import Cache, Language
from fastapi import APIRouter
from fastapi_cache.decorator import cache
from presenters.aging_mechanism import AgingMechanism

from api.db.dao import AgingMechanismDAO

router = APIRouter()


@router.get('/aging-mechanisms', response_model=List[AgingMechanism])
@cache(expire=int(Cache.expire), namespace=Cache.namespace)
async def get_aging_mechanisms(lang: Language = Language.en):
    return loads(AgingMechanismDAO().get_all(lang=lang.value)[0]['jsonobj'])
