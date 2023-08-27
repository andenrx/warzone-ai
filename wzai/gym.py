from . import api
from .agent import Agent
from .orders import Order
from .types import MapState
from .utils import first

from time import time, sleep
from typing import Optional, Tuple, Any, List
import gymnasium as gym

StepResult = Tuple[Any, float, bool, bool, Any]

class Game(gym.Env):
    mapstate: MapState
    turn: int
    def reset(self, seed, options): super().reset()
    def step(self, action): raise NotImplementedError()
    def info(self): return { "turn": self.turn }

    def play(self, agent: Agent, seed=None, options={}):
        state, info = self.reset(seed, options)
        reward = 0
        done = False
        while not done:
            self.display()
            state, reward, terminated, truncated, info = self.step(agent(state))
            done = terminated or truncated
        return reward

class BotGame(Game):
    def __init__(self):
        self.reset()

    def reset(self, seed=None, options={}):
        super().reset(seed=seed, options=options)
        self.turn = 0
        self.mapid = options.get("mapid", api.MapID.SMALL_EARTH)
        self.gameid = api.create_game([1, "AI@warlight.net"], botgame=True, mapid=self.mapid)
        self.mapstruct = api.map_structure(self.gameid, botgame=True)
        self.mapstate = api.map_state(self.gameid, mapstruct=self.mapstruct, playerid=1, botgame=True)
        return self.mapstate, self.info()

    def step(self, action: List[Order]) -> StepResult:
        api.send_orders(self.gameid, self.mapstruct, orders=action, turn=self.turn + 1, playerid=1, botgame=True)
        self.mapstate = api.map_state(self.gameid, self.mapstruct, playerid=1, botgame=True)

        self.turn += 1
        winner = self.winner()

        return self.mapstate, 1 if winner == 1 else -1 if winner == 2 else 0, winner is not None, False, self.info()

    def winner(self) -> Optional[int]:
        info = api.game_info(self.gameid, botgame=True)
        players = [
                player
                for player, player_info in info["players"].items()
                if player_info["state"] == "Playing"
        ]
        if len(players) == 1:
            return players[0]
        else:
            return None

    def display(self):
        print(f"Turn {self.turn}:")
        print(f"  Territories: {(self.mapstate.owner == 1).sum()} : {(self.mapstate.owner == 2).sum()}")
        print(f"  Armies: {self.mapstate.armies[self.mapstate.owner == 1].sum()} : {self.mapstate.armies[self.mapstate.owner == 2].sum()}")
        print(f"  Income: {self.mapstate.income(1)} : {self.mapstate.income(2)}")

class PlayerGame(Game):
    def reset(self, seed=None, options={}):
        super().reset(seed=seed, options=options)
        self.turn = 0
        self.mapid = options.get("mapid", api.MapID.SMALL_EARTH)
        if options.get("resume") is None:
            self.gameid = api.create_game(["me", options["player"]], botgame=False, mapid=self.mapid)
            print(f"Started game: https://www.warzone.com/MultiPlayer?GameID={self.gameid}")
        else:
            self.gameid = options.get("resume")
            info = api.game_info(self.gameid, botgame=False)
            print(f"Resuming game: https://www.warzone.com/MultiPlayer?GameID={self.gameid}")
            self.turn = info["turn"] - 1
        self.mapstruct = api.map_structure(self.gameid, botgame=False)
        self.p1 = api.BOT_ID
        self.mapstate = self.get_mapstate_blocking()
        self.p2 = first(p for p in self.mapstate.owner if p not in { self.p1, 0 })
        return self.mapstate, self.info()

    def get_mapstate_blocking(self, timeout=60, delay=5):
        start = time()
        while time() - start < timeout:
            sleep(delay)
            try:
                return api.map_state(self.gameid, mapstruct=self.mapstruct, playerid=self.p1, botgame=False)
            except api.ServerException:
                print(f"Waiting on player's turn {self.turn}")

    def step(self, action: List[Order]) -> StepResult:
        sleep(10)
        api.send_orders(self.gameid, self.mapstruct, orders=action, turn=self.turn + 1, playerid=self.p1, botgame=False)
        self.mapstate = self.get_mapstate_blocking()

        self.turn += 1
        winner = self.winner()

        return self.mapstate, 1 if winner == self.p1 else -1 if winner == self.p2 else 0, winner is not None, False, self.info()

    def winner(self) -> Optional[int]:
        info = api.game_info(self.gameid, botgame=False)
        players = [
                player
                for player, player_info in info["players"].items()
                if player_info["state"] == "Playing"
        ]
        if len(players) == 1:
            return players[0]
        else:
            return None

    def display(self):
        print(f"Turn {self.turn}:")
        print(f"  Territories: {(self.mapstate.owner == self.p1).sum()} : {(self.mapstate.owner == self.p2).sum()}")
        print(f"  Armies: {self.mapstate.armies[self.mapstate.owner == self.p1].sum()} : {self.mapstate.armies[self.mapstate.owner == self.p2].sum()}")
        print(f"  Income: {self.mapstate.income(self.p1)} : {self.mapstate.income(self.p2)}")
