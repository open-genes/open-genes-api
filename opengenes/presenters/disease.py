from pydantic import BaseModel


class DiseaseShort(BaseModel):
    icd_id: str
    name: str


class Disease(BaseModel):
    id: int
    icd_code: int
    name: str
    icd_name: str


class DiseaseCategories(BaseModel):
    icd_cod: str
    icd_category_name: str
