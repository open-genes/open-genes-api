from pydantic.dataclasses import dataclass


@dataclass
class TaxonOutput:
    id: int
    name: str
