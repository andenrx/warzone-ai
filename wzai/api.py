from .orders import Order
from .types import Bonus, MapStructure, MapState
from .utils import random_name

from enum import IntEnum
from typing import Union, List, Optional
import json
import networkx as nx
import numpy as np
import requests

ROOT = "http://aiserver.warzone.com/api/"
BOT_ID = 633947

Player = Union[str, int]

class MapID(IntEnum):
    # Map ids, sorted from smallest to largest
    BANANA = 29633 # 12, 4
    OWL_ISLAND = 56763 # 12, 4
    NEW_ZEALAND_SMALL = 38436 # 18, 8
    TANZANIA = 51119 # 19, 5
    ITALY = 3448 # 20, 10
    ICELAND = 24221 # 24, 7
    BRITISH_ISLES = 36084 # 25, 6
    FINLAND = 34615 # 31, 6
    PLATEAUS = 55574 # 32, 11
    APPLE = 32414 # 36, 13
    SMALL_EARTH = 70306 # 42, 6
    SPQR = 96770 # 45, 8
    UNITED_STATES = 149 # 48, 10
    MIDDLE_EAST = 92434 # 50, 8
    NORTH_AMERICA = 92435 # 54, 9
    IMPERIUM_ROMANUM = 72163 # 106, 31
    MEDIUM_EARTH = 19785 # 129, 27
    MIDDLE_EARTH = 96728 # 269, 150 (89 non-zero)
    RISE_OF_ROME = 16114 # 273, 83
    AMERICAN_REVOLUTION = 80849 # 500, 222

def create_game(players: List[Player], botgame: bool = False, mapid: int = MapID.SMALL_EARTH) -> int:
    return call(
        "CreateBotGame" if botgame else "CreateGame",
        {
            "gameName": random_name(),
            "players": [
                { "token": _handle_token(player) }
                for player in players
            ],
            "settings": {
                "Fog": "NoFog",
                "MaxCardsHold": 999,
                "ReinforcementCard": "none",
                "OrderPriorityCard": "none",
                "OrderDelayCard": "none",
                "BlockadeCard": "none",
                "AutomaticTerritoryDistribution": "Automatic",
                "OneArmyStandsGuard": False,
                "TerritoryLimit": 2,
                "InitialPlayerArmiesPerTerritory": 2,
                "Wastelands": {
                    "NumberOfWastelands": 0,
                    "WastelandSize": 10,
                },
                "Map": mapid,
            }
        }
    )["gameID"]

def map_structure(gameid: int, botgame: bool = False):
    return _to_map_structure(
        call(
            "GetBotGameSettings" if botgame else "GetGameSettings",
            {"gameID": gameid}
        )["map"]
    )

def map_state(gameid: int, mapstruct: Optional[MapStructure] = None, playerid: int = 633947, botgame: bool = False, return_turn: bool = False):
    mapstruct = mapstruct or map_structure(gameid, botgame=botgame)
    response = call(
        "GetBotGameInfo" if botgame else "GetGameInfo",
        {
            "gameID": gameid,
            "playerID": playerid
        }
    )
    if isinstance(response["gameInfo"], str):
        raise ServerException(response["gameInfo"])

    standing = response["gameInfo"]["latestStanding"]
    if return_turn:
        return _to_map_state(standing, mapstruct), int(response["game"]["numberOfTurns"])+1
    else:
        return _to_map_state(standing, mapstruct)

def game_info(gameid, botgame=False):
    response = call(
        "GetBotGameInfo" if botgame else "GetGameInfo",
        {"gameID": gameid}
    )
    return {
        "turn": int(response["game"]["numberOfTurns"])+1,
        "players": {
            player["id"]: {
                "state": player["state"],
                "hasCommittedOrders": player["hasCommittedOrders"] == "True"
            }
            for player in response["game"]["players"]
        },
        "state": response["game"]["state"]
    }

def send_orders(gameid: str, mapstruct: MapStructure, orders: List[Order], turn: int, playerid: int = 633947, botgame: bool = False):
    response = call(
        "SendOrdersBotGame" if botgame else "SendOrders",
        {
            "gameID": gameid,
            "turnNumber": turn,
            "orders": [ order._encode(mapstruct) for order in orders],
            "playerID": playerid
        }
    )
    return response

def get_replay(gameid: str):
    return call("ExportBotGame", {"gameID": gameid})["result"]

def save_replay(gameid: str, location: str):
    xml = get_replay(gameid)
    with open(location, "w") as file:
        file.write(xml)

def call(api: str, data):
    response = json.loads(requests.post(ROOT + api, json=data).text)
    if "error" in response:
        raise ServerException(response["error"])
    return response

def _handle_token(token: Player):
    if isinstance(token, int):
        return f"00{token}00"
    else:
        return token

def _to_map_structure(data) -> MapStructure:
    g = nx.Graph()

    old_id_to_new_id = {}
    for i, src in enumerate(data["territories"]):
        g.add_node(i, name=src["name"], old_id=int(src["id"]))
        old_id_to_new_id[int(src["id"])] = i

    for i, src in enumerate(data["territories"]):
        for dst in src["connectedTo"]:
            g.add_edge(i, old_id_to_new_id[dst])

    bonuses = []
    for bonus_data in data["bonuses"]:
        bonuses.append(Bonus(
            bonus_data["name"],
            { old_id_to_new_id[i] for i in bonus_data["territoryIDs"] },
            int(bonus_data["value"])
        ))

    return MapStructure(int(data["id"]), data["name"], g, bonuses)

def _to_map_state(data, mapstruct: MapStructure) -> MapState:
    assert len(mapstruct) == len(data)
    data_dict = {terr["terrID"]: terr for terr in data}
    data = [data_dict[mapstruct._wz_terr_id(i)] for i in range(len(data))]
    return MapState(
            np.array([int(terr["armies"]) for terr in data]),
            np.array([_parse_owner(terr["ownedBy"]) for terr in data]),
            mapstruct
    )

def _parse_owner(owner: str) -> int:
    if owner == "Neutral":
        return 0
    return int(owner)

class ServerException(Exception): pass

