from json import loads
from typing import List

from config import cache_if_enabled, Language
from fastapi import APIRouter
from presenters.aging_mechanism import AgingMechanism

from api.db.dao import AgingMechanismDAO

router = APIRouter()


@router.get('/aging-mechanisms', response_model=List[AgingMechanism])
@cache_if_enabled
async def get_aging_mechanisms(lang: Language = Language.en):
    return loads(AgingMechanismDAO().get_all(lang=lang.value)[0]['jsonobj'])
