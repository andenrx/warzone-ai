from .orders import Order
from .types import MapState
from .utils import pretty_print

from typing import List

@pretty_print("playerid")
class Agent:
    def __init__(self, playerid: int):
        self.playerid = playerid

    def __call__(self, mapstate: MapState) -> List[Order]:
        raise NotImplementedError()
