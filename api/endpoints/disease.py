from typing import List
from api.db.dao import GeneSuggestionDAO
from api.models.gene import DiseaseSearchInput, DiseaseSearchOutput

from config import Language
from db.dao import DiseaseDAO
from fastapi import APIRouter, HTTPException, Depends
from models.gene import Disease, DiseaseCategory

router = APIRouter()


@router.get('/disease', response_model=DiseaseSearchOutput)
async def get_disease_list(
    input: DiseaseSearchInput = Depends(DiseaseSearchInput)
) -> List :

    if not any((input.byGeneId, input.byGeneSymbol, input.bySuggestions)):
        raise HTTPException(
            status_code=400,
            detail='At least one parameter shold be provided: byGeneId, byGeneSymbol, bySuggestions',
        )
    
    if input.bySuggestions is not None:
        sls = GeneSuggestionDAO().search(input.bySuggestions, suggestHidden=0)
        idls = []
        for item in sls['items']:
            idls.append(item['id'])
        suggfilter = ','.join(str(f) for f in idls) if idls else input.bySuggestions
        input.bySuggestions = None
        input.byGeneId = suggfilter
    
    return DiseaseDAO().get_by_gene(input)



@router.get(
    '/disease-category',
    response_model=List[DiseaseCategory],
)
async def get_disease_category_list(lang: Language = Language.en):
    raise HTTPException(
        status_code=404,
        detail='Not implemented',
    )
    return DiseaseDAO().get()
