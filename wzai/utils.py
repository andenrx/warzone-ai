from __future__ import annotations

from . import api
from . import types

from typing import Iterable, TypeVar, Optional
from wonderwords import RandomWord
import os
import pickle

def load_mapstruct(mapid: int, cache: str = None) -> game_types.MapStructure:
    """Download a map or load it from a cache"""
    if cache is not None:
        os.makedirs(cache, exist_ok=True)
        if os.path.isfile(f"{cache}/{mapid}.pkl"):
            return pickle.load(open(f"{cache}/{mapid}.pkl", "rb"))

    # The only way to download map data seems to be by creating a game
    gameid = api.create_game([1, 2], botgame=True, mapid=mapid)
    mapstruct = api.map_structure(gameid, botgame=True)
    
    if cache is not None:
        pickle.dump(mapstruct, open(f"{cache}/{mapid}.pkl", "wb"))
    return mapstruct

def random_name():
    return RandomWord().word(include_parts_of_speech=["adjective"]) + "-" + RandomWord().word(include_parts_of_speech=["noun"])

def pretty_print(*attrs: str):
    def handler(c):
        def __repr__(self) -> str:
            return f"{c.__name__}(" + ", ".join(f"{attr}={getattr(self, attr, None)!r}" for attr in attrs) + ")"
        c.__repr__ = __repr__
        return c
    return handler

T = TypeVar("T")
def first(elems: Iterable[T]) -> Optional[T]:
    return next(iter(elems), None)

def chain(*fns: Callable[[T], T]) -> Callable[[T], T]:
    def chained(arg: T) -> T:
        for fn in fns:
            arg = fn(arg)
        return arg
    return chained
