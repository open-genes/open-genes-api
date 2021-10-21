from json import loads
from re import match
from typing import List

from fastapi import APIRouter, HTTPException

from opengenes.config import Language
from opengenes.db.dao import GeneDAO
from opengenes.db.request_handler import RequestHandler
from opengenes.db.sql_raws.scripts import GENES_QUERY
from opengenes.presenters.gene import GeneShort, Gene

router = APIRouter()


@router.get(
    '/gene/search',
)
async def get_genes_list(
        lang: Language = Language.en, page: int = None, pageSize: int = None, byDiseases: str = None,
        byDiseaseCategories: str = None, byAgeRelatedProcess: str = None, byExpressionChange: str = None
):
    sql_handler = RequestHandler(GENES_QUERY)
    sql_handler.set_language(lang.value)
    sql_handler.set_pagination(page, pageSize)
    filters = {}
    if byDiseases:
        filters['diseases'] = byDiseases
    if byDiseaseCategories:
        filters['disease_categories'] = byDiseaseCategories
    if byAgeRelatedProcess:
        filters['functional_clusters'] = byAgeRelatedProcess
    if byExpressionChange:
        filters['expression_change'] = byExpressionChange
    sql_handler.add_filters(sql_handler.validate_filters(filters))
    print(sql_handler.sql)
    return loads(GeneDAO().get_list(request=sql_handler.sql)[0]['respJS'])


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

