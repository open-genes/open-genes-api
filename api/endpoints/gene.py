import pandas as pd
from typing import List

from config import Language, cache_if_enabled
from db.dao import GeneDAO, GeneSuggestionDAO, TaxonDAO

from fastapi import APIRouter, Depends, HTTPException, Query
from models.gene import GeneSearchInput, GeneSearchOutput, GeneSingle, GeneSingleInput
from presenters.gene import (
    Gene,
    GeneForMethylation,
    GeneShort,
    GeneSuggestionOutput,
    GeneSymbolsOutput,
    GeneWithResearches,
)
from presenters.taxon import TaxonOutput
from json import loads


router = APIRouter()


@router.get('/gene/search', response_model=GeneSearchOutput)
@cache_if_enabled
async def gene_search(input: GeneSearchInput = Depends(GeneSearchInput)) -> List:

    if input.bySuggestions is not None:
        sls = GeneSuggestionDAO().search(input.bySuggestions, suggestHidden=0)
        idls = []
        for item in sls['items']:
            idls.append(item['id'])
        suggfilter = ','.join(str(f) for f in idls) if idls else input.bySuggestions
        input.bySuggestions = None
        input.byGeneId = suggfilter

    search_result = GeneDAO().search(input)

    for item in search_result.get("items", []):
        if item["agingMechanisms"]:
            item["agingMechanisms"] = pd.DataFrame(item["agingMechanisms"], dtype=object).drop_duplicates().sort_values(by=['id', 'uuid'], ascending=True).to_dict('records')
    
    return search_result


@router.get(
    '/gene/suggestions',
    response_model=GeneSuggestionOutput,
)
@cache_if_enabled
async def get_gene_suggestions(
    input: str = None,
    byGeneId: str = None,
    byGeneSymbol: str = None,
    suggestHidden: int = Query(default=0, ge=0, le=1),
):
    if not any((byGeneId, byGeneSymbol, input)):
        raise HTTPException(
            status_code=400,
            detail='At least one parameter shold be provided: byGeneId, byGeneSymbol, input',
        )
    elif byGeneSymbol:
        return GeneSuggestionDAO().search_by_genes_symbol(byGeneSymbol, suggestHidden)
    elif byGeneId:
        return GeneSuggestionDAO().search_by_genes_id(byGeneId, suggestHidden)
    else:
        return GeneSuggestionDAO().search(input, suggestHidden)


@router.get(
    '/gene/symbols',
    response_model=List[GeneSymbolsOutput],
)
@cache_if_enabled
async def get_gene_symbols():
    req = GeneDAO().get_symbols()
    rs = [{'id': data[0], 'symbol': data[1]} for data in req]
    return rs


@router.get(
    '/gene/by-latest',
    response_model=List[GeneShort],
)
async def get_gene_by_latest(lang: Language = Language.en):
    raise HTTPException(
        status_code=404,
        detail='Not implemented',
    )
    return GeneDAO().get()


@router.get(
    '/gene/by-functional_cluster/{ids}',
    response_model=List[GeneShort],
)
async def get_gene_by_functional_cluster(ids: str, lang: Language = Language.en):
    raise HTTPException(
        status_code=404,
        detail='Not implemented',
    )
    return GeneDAO().get()


@router.get(
    '/gene/by-selection-criteria/{ids}',
    response_model=List[GeneShort],
)
async def get_gene_by_selection_criteria(ids: str, lang: Language = Language.en):
    raise HTTPException(
        status_code=404,
        detail='Not implemented',
    )
    return GeneDAO().get()


@router.get(
    '/gene/by-go-term/{term}',
    response_model=List[GeneShort],
)
async def get_gene_by_go_term(term: str, lang: Language = Language.en):
    raise HTTPException(
        status_code=404,
        detail='Not implemented',
    )
    return GeneDAO().get()


@router.get(
    '/gene/by-expression-change/{expression_change}',
    response_model=List[GeneShort],
)
async def get_gene_by_expression_change(expression_change: str, lang: Language = Language.en):
    raise HTTPException(
        status_code=404,
        detail='Not implemented',
    )
    return GeneDAO().get()


@router.get('/gene/taxon', response_model=List[TaxonOutput])
async def get_taxon():
    return loads(TaxonDAO().get_all()[0]['jsonobj'])


@router.get('/gene/{id_or_symbol}', response_model=GeneSingle)
@cache_if_enabled
async def gene_search(
    id_or_symbol: int | str, input: GeneSingleInput = Depends(GeneSingleInput)
) -> GeneSingle:
    if isinstance(id_or_symbol, int):
        input.byGeneId = id_or_symbol
    if isinstance(id_or_symbol, str):
        input.bySymbol = id_or_symbol
    search_result = GeneDAO().single(input)
    if not search_result:
        raise HTTPException(
            status_code=404,
            detail='Gene not found',
        )
    if search_result["agingMechanisms"]:
        search_result["agingMechanisms"] = pd.DataFrame(search_result["agingMechanisms"], dtype=object).drop_duplicates().sort_values(by=['id', 'uuid'], ascending=True).to_dict('records')
    return search_result


@router.get(
    '/gene/{symbol}',
    response_model=Gene,
)
async def dummy_get_gene_by_symbol(symbol: str, lang: Language = Language.en):
    raise HTTPException(
        status_code=404,
        detail='Not implemented',
    )


@router.get(
    '/test/gene/{symbol}',
    response_model=Gene,
    include_in_schema=False,
)
async def get_gene_by_symbol(symbol: str, lang: Language = Language.en):
    if not symbol.isnumeric():
        raise HTTPException(
            status_code=404,
            detail='Not implemented',
        )
        return GeneDAO().get()
    ncbi_id = int(symbol)
    try:
        return GeneDAO().get(ncbi_id=ncbi_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=e.args[0])


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



