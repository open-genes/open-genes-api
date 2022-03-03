import os
import pathlib
from enum import Enum

from dotenv import load_dotenv, dotenv_values

load_dotenv(os.path.join(pathlib.Path(__file__).parent.resolve().parent, '.env'))
CONFIG = dict(os.environ)

for k in ['DEBUG','RELOAD']:
    if k in CONFIG: CONFIG[k]=CONFIG[k].lower() in ['true','1','yes','enable']

VERSION = {}
version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '/VERSION')
if os.path.exists(version_file):
    VERSION = dotenv_values(version_file)
    VERSION['major'] = 0
    VERSION['minor'] = 3


class Language(Enum):
    ru = "ru"
    en = "en"


class SortVariant(Enum):
    criteriaQuantity = "criteriaQuantity"
    familyPhylum = "familyPhylum"
    default = "default"
