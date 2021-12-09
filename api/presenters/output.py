from typing import List

from presenters.gene import GeneWithDiet
from presenters.options import Options
from pydantic.dataclasses import dataclass


@dataclass
class DietOutput:
    options: Options
    items: List[GeneWithDiet]
