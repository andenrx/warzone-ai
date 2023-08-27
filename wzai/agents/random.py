from ..agent import Agent
from ..orders import Order, DeployOrder, AttackTransferOrder
from ..types import MapState
from ..utils import chain
from .helper import collect_deploys, collect_attacks

from typing import List
import numpy as np
import random

class Random(Agent):
    def __call__(self, state: MapState) -> List[Order]:
        deploys = self._deploys(state)
        attacks = self._attacks(chain(*deploys)(state))
        return [*deploys, *attacks]

    def _deploys(self, state: MapState) -> List[DeployOrder]:
        owned_territories, = np.where(state.owner == self.playerid)
        return collect_deploys(
                self.playerid,
                random.choices(owned_territories.tolist(), k=state.income(self.playerid))
        )
    
    def _attacks(self, state: MapState) -> List[AttackTransferOrder]:
        owned_territories, = np.where(state.owner == self.playerid)
        return collect_attacks(
                self.playerid,
                [
                    (src, dst)
                    for src in owned_territories
                    for dst in random.choices(list(state.neighbors(src)), k=state.armies[src])
                ]
        )
