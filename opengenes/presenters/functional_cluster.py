from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class FunctionalCluster:
    id: int
    name: str = Field(title="Name of the age-related process/system the gene involved in")

    def __init__(self, id, name_en, name_ru, lang='en', **kwargs):
        self.id = id
        self.name = name_en if lang == 'en' else name_ru
