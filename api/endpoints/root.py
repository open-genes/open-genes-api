from fastapi import APIRouter, HTTPException
from fastapi import Depends
from db.dao import ModelOrganismDAO
from typing import List

router = APIRouter()

from models import LanguageInput
from models.various import ModelOrganism

@router.get(
    '/model-organism',
    response_model=List[ModelOrganism]
)
async def model_organism(input:LanguageInput=Depends(LanguageInput))->List:

    return ModelOrganismDAO().list(input)
