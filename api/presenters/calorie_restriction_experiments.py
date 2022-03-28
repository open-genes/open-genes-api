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
    duration: int
    durationUnit: str
    age: str
    ageUnit: str
    organism: str
    line: str
    sex: str
    tissue: str
    experimentGroupQuantity: str
    doi: str
    expressionChangePercent: float
    isoform: Optional[str]
