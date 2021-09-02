import os
import sys
from enum import Enum

from dotenv import dotenv_values

CONFIG = dotenv_values(os.path.join(sys.path[1], '.env'))


class Language(Enum):
    ru = "ru"
    en = "en"