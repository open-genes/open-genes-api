from pydantic import BaseModel, Field


class Expression(BaseModel):
    name: str = Field(title="Name of the tissue or organ")
    exp_rpkm: str = Field(title="Expression value change in RPKM")
