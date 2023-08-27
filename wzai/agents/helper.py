from typing import List, Callable, TypeVar, Tuple
from collections import defaultdict
from ..orders import Order, DeployOrder, AttackTransferOrder

def collect_deploys(playerid: int, territories: List[int]) -> List[DeployOrder]:
    dedupe: defaultdict[int, int] = defaultdict(int)
    for terr in territories:
        dedupe[terr] += 1
    return [
        DeployOrder(playerid, terr, armies)
        for terr, armies in dedupe.items()
    ]

def collect_attacks(playerid: int, attacks: List[Tuple[int, int]]) -> List[AttackTransferOrder]:
    dedupe: defaultdict[Tuple[int, int], int] = defaultdict(int)
    for attack in attacks:
        dedupe[attack] += 1
    return [
        AttackTransferOrder(playerid, src, dst, armies)
        for (src, dst), armies in dedupe.items()
    ]
