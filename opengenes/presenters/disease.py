from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import Optional


@dataclass
class DiseaseShort:
    icd_id: str = Field(title="ICD code for a disease category")
    name: str = Field(title="Disease name")


@dataclass
class Disease:
    id: int
    icd_code: int = Field(title="ICD code for a disease category")
    name: str = Field(title="Disease name")
    icd_name: str = Field(title="Disease name according to ICD")


@dataclass
class DiseaseCategories:
    icd_cod: str = Field(title="ICD code for a disease category")
    icd_category_name: Optional[str] = Field(title="Disease category name")