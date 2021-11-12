from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class Expression:
    name: str = Field(title="Name of the tissue or organ")
    exp_rpkm: str = Field(title="Expression value change in RPKM")
