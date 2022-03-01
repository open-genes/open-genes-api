from json import loads
from typing import List

from config import Language
from presenters.protein_class import ProteinClass
from fastapi import APIRouter
from api.db.dao import FunctionalClusterDAO

router = APIRouter()


@router.get(
    '/protein-classes',
    response_model=List[ProteinClass]
)
async def get_age_related_processes(lang: Language = Language.en):
    return loads(FunctionalClusterDAO().get_all(lang=lang.value)[0]['jsonobj'])