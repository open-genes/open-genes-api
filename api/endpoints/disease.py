from typing import List

from config import Language
from db.dao import DiseaseDAO
from fastapi import APIRouter, HTTPException
from presenters.disease import Disease, DiseaseCategories

router = APIRouter()


@router.get(
    '/disease',
    response_model=List[Disease],
)
async def get_disease_list(lang: Language = Language.en):
    raise HTTPException(
        status_code=404,
        detail='Not implemented',
    )
    return DiseaseDAO().get()


@router.get(
    '/disease-category',
    response_model=List[DiseaseCategories],
)
async def get_disease_category_list(lang: Language = Language.en):
    raise HTTPException(
        status_code=404,
        detail='Not implemented',
    )
    return DiseaseDAO().get()
