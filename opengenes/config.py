import os
import pathlib
from enum import Enum

from dotenv import load_dotenv

load_dotenv(os.path.join(pathlib.Path(__file__).parent.resolve().parent, '.env'))
CONFIG = os.environ

class Language(Enum):
    ru = "ru"
    en = "en"
