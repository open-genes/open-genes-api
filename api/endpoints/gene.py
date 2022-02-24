import json
from json import loads
from typing import List

from fastapi import APIRouter, HTTPException

from config import Language, SortVariant
from db.dao import GeneDAO, GeneSuggestionDAO
from db.request_handler import RequestHandler
from presenters.gene import GeneShort, Gene, GeneForMethylation, GeneWithResearches, GeneSuggestion

router = APIRouter()

@router.get(
    '/gene/search',
)
async def gene_search(
        lang: Language = Language.en, page: int = None, pageSize: int = None, byDiseases: str = None,
        byDiseaseCategories: str = None, byAgeRelatedProcess: str = None, byExpressionChange: str = None,
        bySelectionCriteria: str = None, byAgingMechanism: str = None, byProteinClass: str = None,
        bySpecies: str = None, byGeneId: str = None,
        sortBy: SortVariant = SortVariant.default, sortOrder: str = "DESC",
        researches: str=None, isHidden:str = None

):
    lang=lang.value
    sortBy=sortBy.value
    return GeneDAO().search(locals())

@router.get(
    '/gene/suggestions',
    response_model=List[GeneSuggestion],
)
async def get_gene_suggestions(input: str = None):
    if not input:
        return []
    return GeneSuggestionDAO().search(input)

@router.get(
    '/gene/by-latest',
    response_model=List[GeneShort],
)
async def get_gene_by_latest(lang: Language = Language.en):
    raise HTTPException( status_code=404, detail='Not implemented',)
    return GeneDAO().get()


@router.get(
    '/gene/by-functional_cluster/{ids}',
    response_model=List[GeneShort],
)
async def get_gene_by_functional_cluster(ids: str, lang: Language = Language.en):
    raise HTTPException( status_code=404, detail='Not implemented',)
    return GeneDAO().get()


@router.get(
    '/gene/by-selection-criteria/{ids}',
    response_model=List[GeneShort],
)
async def get_gene_by_selection_criteria(ids: str, lang: Language = Language.en):
    raise HTTPException( status_code=404, detail='Not implemented',)
    return GeneDAO().get()


@router.get(
    '/gene/by-go-term/{term}',
    response_model=List[GeneShort],
)
async def get_gene_by_go_term(term: str, lang: Language = Language.en):
    raise HTTPException( status_code=404, detail='Not implemented',)
    return GeneDAO().get()


@router.get(
    '/gene/by-expression-change/{expression_change}',
    response_model=List[GeneShort],
)
async def get_gene_by_expression_change(expression_change: str, lang: Language = Language.en):
    raise HTTPException( status_code=404, detail='Not implemented',)
    return GeneDAO().get()

@router.get( '/gene/{symbol}', response_model=Gene,)
async def dummy_get_gene_by_symbol(symbol: str, lang: Language = Language.en):
        raise HTTPException( status_code=404, detail='Not implemented',)

@router.get(
    '/test/gene/{symbol}',
    response_model=Gene,
    include_in_schema=False,
)
async def get_gene_by_symbol(symbol: str, lang: Language = Language.en):
    if not symbol.isnumeric():
        raise HTTPException( status_code=404, detail='Not implemented',)
        return GeneDAO().get()
    ncbi_id=int(symbol)
    try:
        return GeneDAO().get(ncbi_id=ncbi_id)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=e.args[0],
        )

# dummy endpoint, for docs, actual processing is done in get_gene_by_symbol
@router.get(
    '/gene/{ncbi_id}',
    response_model=Gene,
)
async def get_gene_by_id(ncbi_id: int, lang: Language = Language.en):
    return 'dummy'


@router.get(
    '/gene/methylation',
    response_model=GeneForMethylation,
)
async def get_gene_by_id(ncbi_id: int, lang: Language = Language.en):
    return 'dummy'


@router.get(
    '/gene/increase-lifespan',
    response_model=GeneWithResearches,
)
async def get_gene_by_id(ncbi_id: int, lang: Language = Language.en):
    return 'dummy'
