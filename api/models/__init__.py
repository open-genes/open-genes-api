from pydantic import BaseModel,create_model
from typing import Literal,List

name_counter=0

def ogmodel(*args,**fields):
    name=None
    d=None
    base=None
    for a in args:
        if isinstance(a,str): name=a
        if isinstance(a,type): base=a
        if isinstance(a,tuple): base=a
        if isinstance(a,dict): d=a
    if not d: d={}
    d.update(fields)
    global name_counter
    name_counter=name_counter+1
    base=base if isinstance(base,tuple) else (base,)
    if not name: name='_'.join(b.__name__ for b in base)+'_'+str(name_counter)
    return type(name,base,d)


class PaginationInput(BaseModel):
    page:int|None=1
    pageSize:int|None=10

class SortInput(BaseModel):
    sortOrder: Literal['ASC','DESC']|None = 'DESC'

class LanguageInput(BaseModel):
    lang:Literal['en','ru']|None='en'


class PaginatedOutput(BaseModel):
    options:create_model('PaginationOptions',
            objTotal=(int,...),
            pagination=(create_model('PaginationData',
                page=(int,...),
                pageSize=(int,...),
                pagesTotal=(int,...),
            ),...)
    )
    items:List

class Timestamp(BaseModel):
    created:int |None = 0
    changed:int

