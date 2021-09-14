from pydantic import BaseModel


class DiseaseShort(BaseModel):
    icd_id: str = Field(title="ICD code for a disease category")
    name: str = Field(title="Disease name")


class Disease(BaseModel):
    id: int
    icd_code: int = Field(title="ICD code for a disease category")
    name: str = Field(title="Disease name")
    icd_name: str = Field(title="Disease name according to ICD")


class DiseaseCategories(BaseModel):
    icd_cod: str = Field(title="ICD code for a disease category")
    icd_category_name: str Field(title="Disease category name")
