from typing import List

from fastapi import APIRouter, HTTPException

from opengenes.entities import entities
from opengenes.db import dao

router = APIRouter()


@router.get(
    '/',
    response_model=List[entities.Gene],
)
async def get_genes_list():
    return dao.GeneDAO().get()


@router.get(
    '/{ncbi_id}',
    response_model=entities.Gene,
)
async def get_gene(ncbi_id: int):
    try:
        return dao.GeneDAO().get(ncbi_id=ncbi_id)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=e.args[0],
        )
