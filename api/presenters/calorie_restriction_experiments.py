from pydantic.dataclasses import dataclass
from typing import Optional


@dataclass
class CalorieRestrictionExperiment:
    lexpressionChangeLogFc: float
    pValue: str
    crResult: str
    measurementMethod: str
    measurementType: str
    restrictionPercent: int
    restrictionTime: str
    age: str
    organism: str
    line: str
    sex: str
    tissue: str
    experimentNumber: str
    doi: str
    expressionChangePercent: float
    isoform: Optional[str]
