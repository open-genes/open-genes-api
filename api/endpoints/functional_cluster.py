from json import loads
from typing import List

from config import Language
from presenters.functional_cluster import FunctionalCluster
from fastapi import APIRouter
from api.db.dao import FunctionalClusterDAO

router = APIRouter()


@router.get(
    '/age-related-processes',
    response_model=List[FunctionalCluster]
)
async def get_diet_list(lang: Language = Language.en):
    return loads(FunctionalClusterDAO().get_all(lang=lang.value)[0]['jsonobj'])