from __future__ import annotations

from .utils import pretty_print, first

from itertools import product
from typing import List, Optional, Set, Iterable, Dict
import numpy as np

@pretty_print("name", "value")
class Bonus:
    def __init__(self, name: str, territories: Set[int], value: int):
        self.name: str = name
        self.terr: Set[int] = territories
        self.value: int = value

    def owned_by(self, state: MapState, player: int):
        return all(
            state.owner[i] == player
            for i in self.terr
        )

@pretty_print("name", "mapid")
class MapStructure:
    def __init__(self, mapid: int, name: str, graph, bonuses: List[Bonus]):
        self.mapid = mapid
        self.name = name
        self._graph = graph
        self.bonuses = [bonus for bonus in bonuses if bonus.value != 0]

    def neighbors(self, src: int) -> Iterable[int]:
        return self._graph.neighbors(src)

    def _terr_name(self, terr: int) -> str:
        return self._graph.nodes.get(terr)["name"]
    
    def _wz_terr_id(self, terr: int) -> str:
        return self._graph.nodes.get(terr)["old_id"]

    def __len__(self):
        return len(self._graph.nodes) 

@pretty_print("mapstruct")
class MapState:
    def __init__(self, armies: np.ndarray, owner: np.ndarray, mapstruct: MapStructure):
        assert armies.shape == owner.shape
        self.armies = armies
        self.owner = owner
        self.mapstruct = mapstruct
    
    def __len__(self) -> int:
        return len(self.armies)

    def winner(self) -> Optional[int]:
        return first(player for player in self.owner if player != 0)
        # p = 0
        # for owner in self.owner:
        #     if owner != 0 and p == 0:
        #         # first non-neutral player
        #         p = owner
        #     elif owner != p and owner != 0 != p:
        #         # two different players are left
        #         return None
        # return p

    def neighbors(self, src: int, include_self: bool = False) -> List[int]:
        return list(self.mapstruct.neighbors(src)) + ([src] if include_self else [])

    def owned_by(self, playerid: int) -> List[Int]:
        return np.where(self.owner == playerid)[0].tolist()

    def borders(self, player: int, include_neutrals=True) -> List[int]:
        return [
            src for src in range(len(self))
            if self.owner[src] == player
            and any(
                self.owner[dst] != player
                and (include_neutrals or self.owner[dst] != 0)
                for dst in self.neighbors(src)
            )
        ]

    def copy(self) -> MapState:
        return MapState(
            self.armies.copy(),
            self.owner.copy(),
            self.mapstruct
        )

    def assert_valid(self):
        assert (self.armies >= 0).all()
        assert len(self.armies) == len(self.owner) == len(self.mapstruct)

    def income(self, player: int) -> int:
        n = 5
        for bonus in self.mapstruct.bonuses:
            if bonus.owned_by(self, player):
                n += bonus.value
        return n

    def total_armies(self, player: int) -> int:
        return self.armies[self.owner == player].sum()

