from json import loads
from typing import List

from config import Language
from presenters.aging_mechanism import AgingMechanism
from fastapi import APIRouter
from api.db.dao import AgingMechanismDAO

router = APIRouter()


@router.get(
    '/aging-mechanisms',
    response_model=List[AgingMechanism]
)
async def get_aging_mechanisms(lang: Language = Language.en):
    return loads(AgingMechanismDAO().get_all(lang=lang.value)[0]['jsonobj'])
