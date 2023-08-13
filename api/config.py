import os
import pathlib
from dataclasses import dataclass
from enum import Enum

from dotenv import dotenv_values, load_dotenv
from fastapi_cache.decorator import cache

load_dotenv(os.path.join(pathlib.Path(__file__).parent.resolve().parent, '.env'))
CONFIG = dict(os.environ)

for k in ['DEBUG', 'RELOAD', 'ENABLE_CACHE']:
    if k in CONFIG:
        CONFIG[k] = CONFIG[k].lower() in ['true', '1', 'yes', 'enable']

VERSION = {}
version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '/VERSION')
if os.path.exists(version_file):
    VERSION = dotenv_values(version_file)
    VERSION['major'] = 0
    VERSION['minor'] = 4


class Language(Enum):
    ru = "ru"
    en = "en"


class SortVariant(Enum):
    criteriaQuantity = "criteriaQuantity"
    familyPhylum = "familyPhylum"
    default = "default"


@dataclass
class Cache:
    expire = CONFIG.get('CACHE_EXPIRE')
    namespace = CONFIG.get('CACHE_NAMESPACE')
    secret_token = CONFIG.get('CACHE_SECRET_TOKEN')
    enable_cache = CONFIG.get('ENABLE_CACHE')


def cache_if_enabled(func):
    if Cache.enable_cache:
        return cache(expire=int(Cache.expire), namespace=Cache.namespace)(func)
    else:
        return func
