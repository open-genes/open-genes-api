from pydantic import BaseModel
from models import *

class ModelOrganism(BaseModel):
    id:int
    latinName:str|None
    name:str|None
    _select={
        'id':"model_organism.id",
        'latinName':"model_organism.name_lat",
        'name':"model_organism.name_@LANG@",
    }
    _from=""" from model_organism """
    _order_by="model_organism.id"


