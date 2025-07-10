import httpx
from .models import FlagMeta
from functools import lru_cache
import asyncio


class FlagNotFound(Exception):
    pass


# Simple in-memory cache (not persistent, for demo)
_cache = {}


async def get_flag(country: str) -> FlagMeta:
    key = country.lower().strip()
    if key in _cache:
        return _cache[key]
    # Simulate API call (replace with real REST Countries API in prod)
    if key in ("canada", "ca"):
        meta = FlagMeta(country="Canada", code="CA", flag_url="https://flagcdn.com/ca.svg")
    else:
        raise FlagNotFound(f"Flag not found for '{country}'")
    _cache[key] = meta
    return meta
