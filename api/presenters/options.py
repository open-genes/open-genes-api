from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class Pagination:
    page: int = Field()
    pageSize: int = Field()
    pagesTotal: int = Field()


@dataclass
class Options:
    objTotal: int = Field()
    pagination: Pagination = Field()
