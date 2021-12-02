from pydantic.dataclasses import dataclass
from typing import Optional


@dataclass
class CalorieRestrictionExperiment:
    id: int
    gene_id: Optional[int]
    p_val: Optional[str] = None
    result: Optional[str] = None
    measurement_method: Optional[int] = None
    measurement_type: Optional[int] = None
    restriction_percent: Optional[float] = None
    restriction_time: Optional[int] = None
    restriction_time_unit: Optional[int] = None
    age: Optional[str] = None
    age_time_unit: Optional[int] = None
    model_organism: Optional[int] = None
    strain: Optional[int] = None
    organism_sex: Optional[int] = None
    tissue: Optional[int] = None
    isoform: Optional[int] = None
    experiment_number: Optional[str] = None
    expression_change_log_fc: Optional[str] = None
    expression_change_percent: Optional[str] = None
    doi: Optional[str] = None
