from typing import List, Literal

from pydantic import BaseModel, create_model

name_counter = 0


def ogmodel(*args, **fields):
    name = None
    base = None
    for a in args:
        if isinstance(a, str):
            name = a
        if isinstance(a, type):
            base = a
        if isinstance(a, tuple):
            base = a
        if isinstance(a, dict):
            d = a
    d = {'__annotations__': {}}

    for f_name, f_def in fields.items():
        f_annotation = f_def if isinstance(f_def, type) else None
        f_annotation = f_def[0] if isinstance(f_def, tuple) else None
        f_value = f_def if not isinstance(f_def, type) else None
        f_value = f_def[1] if isinstance(f_def, tuple) and len(f_def) > 1 else f_value

        d[f_name] = f_value
        if f_annotation:
            d['__annotations__'][f_name] = f_annotation

    global name_counter
    name_counter = name_counter + 1
    base = base if isinstance(base, tuple) else (base,)
    if not name:
        name = '_'.join(b.__name__ for b in base) + '_' + str(name_counter)
    return type(name, base, d)


class PaginationInput(BaseModel):
    page: int | None = 1
    pageSize: int | None = 20


class SortInput(BaseModel):
    sortOrder: Literal['ASC', 'DESC'] | None = 'DESC'


class LanguageInput(BaseModel):
    lang: Literal['en', 'ru'] | None = 'en'


class PaginationData(BaseModel):
    page: int
    pageSize: int
    pagesTotal: int
    _select = {
        'pagesTotal': "objTotal div pageSize+case when objTotal mod pageSize<>0 then 1 else 0 end",
    }


class PaginationOptions(BaseModel):
    objTotal: int
    total: int | None
    pagination: PaginationData


class PaginatedOutput(BaseModel):
    options: PaginationOptions
    items: List
    _name = "_meta"
    _params = [lambda input: input.get('page', 1), lambda input: input.get('pageSize'), 3]
    _from = "from (select coalesce((select row_count from @PRIMARY_TABLE@ limit 1),0) as objTotal, null as total, %s as page, coalesce(nullif(%s,0),(select row_count from @PRIMARY_TABLE@ limit 1)) as pageSize, %s as pagesTotal) s "


class Timestamp(BaseModel):
    created: int | None = 0
    changed: int | None = 0
