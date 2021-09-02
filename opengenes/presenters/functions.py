from pydantic import BaseModel


class Function(BaseModel):
    proteinActivity: str
    proteinActivityObject: str
    processLocalization: str
    comment: str
