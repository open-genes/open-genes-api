import os
import pathlib
from enum import Enum

from dotenv import dotenv_values

CONFIG = dotenv_values(os.path.join(pathlib.Path(__file__).parent.resolve().parent, '.env'))


class Language(Enum):
    ru = "ru"
    en = "en"
