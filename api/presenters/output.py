from typing import List

from presenters.gene import GeneShort, GeneWithDiet
from presenters.options import Options
from pydantic.dataclasses import dataclass


@dataclass
class DietOutput:
    options: Options
    items: List[GeneWithDiet]


@dataclass
class GeneOutput:
    options: Options
    items: List[GeneShort]
