#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from enum import Enum
from typing import Union

from . import context
from .mytypes import Locale


class Chat(Enum):
    WHISPER = 0 # check if bot can lieten to whispered messages
    GLOBAL = 1
    BOTH = 2

class Gamemode(Enum):
    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2

@dataclass
class Player:
    class _Any:
        def __iter__(self):
            return iter(())
    
    gamemode: Gamemode = field(repr = False)
    language: Locale = field(repr = False)
    platform: str = field(repr = False)
    trial: bool = field(repr = False)
    name: str
    user_id: int = field(repr = False)
    
    def __str__(self):
        return self.name
    
    def execute(self, command: str):
        context.BaseContext().execute(f"execute {self.name} ~~~ {command}")
    
    def effect(self, effect_name: str, duration: int = 2147483647):
        context.BaseContext().execute(f"effect {self.name} {effect_name} {duration}")
    
    def parasite(self, message: str):
        self.execute(f"say {message}")
    
    @classmethod
    def fromproperties(cls, properties: dict):
        return cls(
            gamemode = properties["Gamemode"],
            language = properties["Language"],
            platform = properties["Platform"],
            trial = properties["IsTrial"],
            name = properties["Sender"],
            user_id = properties["UserID"]
        )
    
ANY_PLAYER = Player._Any()

class Permission:
    def __init__(self, permission: Union[set, Player._Any] = ANY_PLAYER):
        self.permission = permission
    
    def __in__(self, other: Player):
        return permission == ANY_PLAYER or other.name in iter(permission)
