from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import Optional


@dataclass
class DiseaseShort:
    icd_id: str = Field(title="ICD code for a disease category")
    name: str = Field(title="Disease name")

    def __init__(
        self,
        icd_code,
        name_en=None,
        name_ru=None,
        lang='en',
        **kwargs
    ):
        self.icd_id = icd_code
        self.name = name_en if lang == 'en' else name_ru


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

    def __init__(
        self,
        icd_code_visible,
        icd_name_en=None,
        icd_name_ru=None,
        lang='en',
        **kwargs
    ):
        self.icd_cod = icd_code_visible
        self.icd_category_name = icd_name_en if lang == 'en' else icd_name_ru
