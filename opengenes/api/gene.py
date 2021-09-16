from typing import List

from fastapi import APIRouter, HTTPException

from opengenes.config import Language
from opengenes.db.dao import GeneDAO
from opengenes.presenters.gene import GeneShort, Gene
from opengenes.presenters.origin import Origin

router = APIRouter()


@router.get(
    '/gene/',
    response_model=List[GeneShort],
)
async def get_genes_list(lang: Language):
    output = []
    for gene in GeneDAO().get_list():
        temp_gene = GeneShort(**gene)
        temp_gene.origin = Origin(**GeneDAO().get_origin_for_gene(gene['phylum_id']))
        output.append(temp_gene)
    return output


@router.get(
    '/gene/{ncbi_id}',
    response_model=Gene,
)
async def get_gene(ncbi_id: int, lang: Language):
    try:
        return GeneDAO().get(ncbi_id=ncbi_id)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=e.args[0],
        )


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
