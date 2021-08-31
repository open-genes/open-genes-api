import os
import sys

from dotenv import dotenv_values

CONFIG = dotenv_values(os.path.join(sys.path[1], '.env'))
