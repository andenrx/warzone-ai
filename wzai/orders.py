from __future__ import annotations

from .types import MapState, MapStructure
from .utils import pretty_print

from functools import lru_cache
from typing import Tuple, Dict
import numpy as np

def fixed_round(x: float) -> int:
    return int(np.floor(x + 0.5))

@pretty_print("player")
class Order:
    def __init__(self, player: int):
        self.player = int(player)

    def __call__(self, state: MapState, inplace=False):
        self.assert_valid(state)
        if not inplace:
            state = state.copy()
        state.assert_valid()
        return self._execute(state)
    
    def priority(self) -> int: raise NotImplementedError()
    def assert_valid(self, state: MapState): raise NotImplementedError()

    def _execute(self, state: MapState): raise NotImplementedError()
    def _encode(self, mapstruct: MapStructure) -> Dict[str, object]: raise NotImplementedError()

@pretty_print("player", "src", "dst", "armies")
class AttackTransferOrder(Order):
    def __init__(self, player: int, src: int, dst: int, armies: int):
        super().__init__(player)
        self.src = src
        self.dst = dst
        self.armies = armies

    @staticmethod
    def combat(attack: int, defend: int) -> Tuple[int, int]:
        return fixed_round(attack - defend * 0.7), fixed_round(defend - attack * 0.6)

    def priority(self): return 50

    def _execute(self, state: MapState):
        if state.owner[self.src] != self.player:
            # player no longer owns territory
            return state
        if state.owner[self.src] == state.owner[self.dst]:
            # transfer
            armies = min(self.armies, state.armies[self.src])
            state.armies[self.src] -= armies
            state.armies[self.dst] += armies
        else:
            # attack
            attack = min(self.armies, state.armies[self.src])
            defend = state.armies[self.dst]
            attack_survive, defend_survive = AttackTransferOrder.combat(attack, defend)
            if attack_survive > 0 and defend_survive <= 0:
                # attacker wins
                state.armies[self.src] -= attack
                state.armies[self.dst] = attack_survive
                state.owner[self.dst] = self.player
            else:
                # defender wins
                attack_survive = max(attack_survive, 0)
                state.armies[self.src] -= (attack - attack_survive)
                state.armies[self.dst] = max(defend_survive, 0)
        return state

    def _encode(self, mapstruct: MapStructure) -> Dict[str, object]:
        return {
            "type": "GameOrderAttackTransfer",
            "playerID": self.player,
            "from": mapstruct._wz_terr_id(self.src),
            "to": mapstruct._wz_terr_id(self.dst),
            "numArmies": str(self.armies),
            "attackTeammates": True
        }

    def assert_valid(self, state: MapState):
        assert np.issubdtype(type(self.armies), int)
        assert np.issubdtype(type(self.src), int)
        assert np.issubdtype(type(self.dst), int)
        assert self.dst in state.neighbors(self.src)
        assert self.armies > 0


@pretty_print("player", "target", "armies")
class DeployOrder(Order):
    def __init__(self, player: int, target: int, armies: int):
        super().__init__(player)
        self.target = int(target)
        self.armies = int(armies)

    def priority(self): return 25

    def _execute(self, state):
        state.armies[self.target] += self.armies
        return state

    def _encode(self, mapstruct: MapStructure) -> Dict[str, object]:
        return {
            "type": "GameOrderDeploy",
            "playerID": self.player,
            "armies": str(self.armies),
            "deployOn": mapstruct._wz_terr_id(self.target)
        }

    def assert_valid(self, state: MapState):
        assert np.issubdtype(type(self.armies), int)
        assert np.issubdtype(type(self.target), int)
        assert state.owner[self.target] == self.player
        assert 0 < self.armies <= state.income(self.player)
