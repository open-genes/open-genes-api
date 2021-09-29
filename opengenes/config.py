import os
import sys
from enum import Enum

from dotenv import load_dotenv

load_dotenv(os.path.join(sys.path[1], '.env'))
CONFIG = os.environ

class Language(Enum):
    ru = "ru"
    en = "en"
