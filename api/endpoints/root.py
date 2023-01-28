from typing import List

from db.dao import ModelOrganismDAO
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache

router = APIRouter()

from config import cache_if_enabled
from models import LanguageInput
from models.various import ModelOrganismOutput


@router.get('/model-organism', response_model=ModelOrganismOutput)
@cache_if_enabled
async def model_organism(input: LanguageInput = Depends(LanguageInput)) -> List:

    return ModelOrganismDAO().list(input)
