from fastapi import APIRouter, HTTPException
from fastapi import Depends
from db.dao import ModelOrganismDAO
from typing import List

router = APIRouter()

from models import LanguageInput
from models.various import ModelOrganismOutput

@router.get(
    '/model-organism',
    response_model=ModelOrganismOutput
)
async def model_organism(input:LanguageInput=Depends(LanguageInput))->List:

    return ModelOrganismDAO().list(input)
