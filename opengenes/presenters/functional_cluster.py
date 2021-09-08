from pydantic import BaseModel


class FunctionalCluster(BaseModel):
    id: int
    name: str = Field(title="Name of the age-related process/system the gene involved in")
