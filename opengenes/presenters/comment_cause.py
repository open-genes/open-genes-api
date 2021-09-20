from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class CommentCause:
    name: str = Field()

    def __init__(self, name_en, **kwargs):
        self.name = name_en