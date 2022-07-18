from json import loads
from typing import List

from config import Language
from fastapi import APIRouter
from presenters.functional_cluster import FunctionalCluster

from api.db.dao import FunctionalClusterDAO

router = APIRouter()


@router.get('/age-related-processes', response_model=List[FunctionalCluster])
async def get_age_related_processes(lang: Language = Language.en):
    return loads(FunctionalClusterDAO().get_all(lang=lang.value)[0]['jsonobj'])
