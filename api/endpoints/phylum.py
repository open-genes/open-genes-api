from json import loads
from typing import List

from config import cache_if_enabled
from fastapi import APIRouter
from presenters.phylum import PhylumOutput

from api.db.dao import PhylumDAO

router = APIRouter()


@router.get('/phylum', response_model=List[PhylumOutput])
@cache_if_enabled
async def get_phylum():
    return loads(PhylumDAO().get_all()[0]['jsonobj'])
