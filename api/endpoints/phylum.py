from json import loads
from typing import List

from presenters.phylum import PhylumOutput
from fastapi import APIRouter
from api.db.dao import PhylumDAO

router = APIRouter()


@router.get(
    '/phylum',
    response_model=List[PhylumOutput]
)
async def get_phylum():
    print(loads(PhylumDAO().get_all()[0]['jsonobj']))
    return loads(PhylumDAO().get_all()[0]['jsonobj'])