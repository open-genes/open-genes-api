from json import loads
from re import fullmatch
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
        lang: Language, page: int = None, pagesize: int = None, diseases: str = None,
        disease_categories: str = None, functional_clusters: str = None, expression_change: str = None
):
    sql_handler = RequestHandler(GENES_QUERY)
    sql_handler.set_language(lang.value)
    sql_handler.set_pagination(page, pagesize)
    filters = {}
    if diseases and fullmatch(r"(\d,)?\d", diseases):
        filters['diseases'] = diseases
    if disease_categories and fullmatch(r"(\d,)?\d", disease_categories):
        filters['disease_categories'] = disease_categories
    if functional_clusters and fullmatch(r"(\d,)?\d", functional_clusters):
        filters['functional_clusters'] = functional_clusters
    if expression_change and fullmatch(r"(\d,)?\d", expression_change):
        filters['expression_change'] = expression_change
    sql_handler.add_filters(filters)
    return loads(GeneDAO().get_list(request=sql_handler.sql)[0]['respJS'])


@router.get(
    '/gene/{ncbi_id}',
    response_model=Gene,
)
async def get_gene_by_id(ncbi_id: int, lang: Language):
    try:
        return GeneDAO().get(ncbi_id=ncbi_id)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=e.args[0],
        )


@router.get(
    '/gene/{symbol}',
    response_model=Gene,
)
async def get_gene_by_symbol(symbol: str, lang: Language):
    return GeneDAO().get()


@router.get(
    '/gene/by-latest',
    response_model=List[GeneShort],
)
async def get_gene_by_latest(lang: Language):
    return GeneDAO().get()


@router.get(
    '/gene/by-functional_cluster/{ids}',
    response_model=List[GeneShort],
)
async def get_gene_by_functional_cluster(lang: Language, ids: str):
    return GeneDAO().get()


@router.get(
    '/gene/by-selection-criteria/{ids}',
    response_model=List[GeneShort],
)
async def get_gene_by_selection_criteria(lang: Language, ids: str):
    return GeneDAO().get()


@router.get(
    '/gene/by-go-term/{term}',
    response_model=List[GeneShort],
)
async def get_gene_by_go_term(lang: Language, term: str):
    return GeneDAO().get()


@router.get(
    '/gene/by-expression-change/{expression_change}',
    response_model=List[GeneShort],
)
async def get_gene_by_expression_change(lang: Language, expression_change: str):
    return GeneDAO().get()
