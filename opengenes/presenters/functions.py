from pydantic import BaseModel, Field


class Function(BaseModel):
    proteinActivity: str = Field(title="Protein activity")
    proteinActivityObject: str = Field(title="Protein activity object")
    processLocalization: str = Field(title="Process localization")
    comment: str
