from json import loads
from typing import List

from config import Language
from presenters.aging_mechanism import AgingMechanism
from fastapi import APIRouter
from api.db.dao import AgingMechanismDAO

router = APIRouter()


@router.get(
    '/age-related-processes',
    response_model=List[AgingMechanism]
)
async def get_age_related_processes(lang: Language = Language.en):
    return loads(AgingMechanismDAO().get_all(lang=lang.value)[0]['jsonobj'])
