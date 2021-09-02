from pydantic import BaseModel


class FunctionalCluster(BaseModel):
    id: int
    name: str
