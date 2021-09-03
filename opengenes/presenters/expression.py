from pydantic import BaseModel


class Expression(BaseModel):
    name: str
    exp_rpkm: str
