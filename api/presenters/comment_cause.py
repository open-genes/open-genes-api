from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class CommentCause:
    name: str = Field()

    def __init__(self, name_en, name_ru, lang='en', **kwargs):
        self.name = name_en if lang == 'en' else name_ru
