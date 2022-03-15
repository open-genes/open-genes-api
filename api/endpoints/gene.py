import json
from json import loads
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi import Depends

from config import Language, SortVariant
from db.dao import GeneDAO, GeneSuggestionDAO
from db.request_handler import RequestHandler
from presenters.gene import GeneShort, Gene, GeneForMethylation, GeneWithResearches, GeneSuggestionOutput

router = APIRouter()
def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

class CommonQueryParams2:
    def __init__(self, pageSize: int | None = None, page: int = 1):
        self.pageSize = pageSize
        self.page = page

from models.gene import GeneSearchInput,GeneSearched

@router.get(
    '/gene/search',
    response_model=GeneSearched
)
async def gene_search(input:GeneSearchInput=Depends(GeneSearchInput))->List:
    #
    if input.bySuggestions is not None:
        sls = GeneSuggestionDAO().search(input.bySuggestions)
        idls = []
        for item in sls['items']:
            idls.append(item['id'])
        suggfilter = ','.join(str(f) for f in idls)
        input.bySuggestions = None
        input.byGeneId = suggfilter
    #
    return GeneDAO().search(input)

@router.get(
    '/gene/suggestions',
    response_model=GeneSuggestionOutput,
)
async def get_gene_suggestions(input: str = None, byGeneId: str = None, byGeneSmb: str = None):
    if byGeneSmb:
        return GeneSuggestionDAO().search_by_genes_symbol(byGeneSmb)
    elif byGeneId:
        return GeneSuggestionDAO().search_by_genes_id(byGeneId)
    else:
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
    # response_model=Gene,
    # include_in_schema=False,
)
async def get_gene_by_symbol(symbol: str, lang: Language = Language.en):
    if not symbol.isnumeric():
        return GeneDAO().get_gene_page(symbol)

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
