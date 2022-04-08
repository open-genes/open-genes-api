from json import loads
from typing import List

from config import Language
from presenters.protein_class import ProteinClass
from fastapi import APIRouter
from api.db.dao import ProteinClassDAO

router = APIRouter()


@router.get(
    '/protein-class',
    response_model=List[ProteinClass]
)
async def get_protein_class(lang: Language = Language.en):
    return loads(ProteinClassDAO().get_all(lang=lang.value)[0]['jsonobj'])