from typing import List

from fastapi import APIRouter

from opengenes.config import Language
from opengenes.db.dao import DiseaseDAO
from opengenes.presenters.disease import Disease, DiseaseCategories

router = APIRouter()


@router.get(
    '/disease',
    response_model=List[Disease],
)
async def get_disease_list(lang: Language):
    return DiseaseDAO().get()


@router.get(
    '/disease-category',
    response_model=List[DiseaseCategories],
)
async def get_disease_category_list(lang: Language):
    return DiseaseDAO().get()
