from typing import List

from presenters.gene import GeneShort
from presenters.options import Options
from pydantic.dataclasses import dataclass


@dataclass
class PhylumOutput:
    id: int
    name: str
    age: str
    order: int
