from .types import MapStructure, MapState

import torch
import torch_geometric as pyg

def from_mapstruct(mapstruct: MapStructure) -> torch.Tensor:
    return pyg.utils.add_self_loops(
        pyg.utils.from_networkx(
            mapstruct._graph
        ).edge_index
    )[0]

def from_mapstate(mapstate: MapState) -> torch.Tensor:
    return torch.stack([
        torch.tensor(mapstate.armies, dtype=torch.float),
        torch.tensor(mapstate.owner == 1, dtype=torch.float),
        torch.tensor(mapstate.owner == 2, dtype=torch.float),
        torch.tensor(mapstate.owner == 0, dtype=torch.float),
    ], dim=1)
