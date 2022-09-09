#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
import re
from uuid import uuid4

from .msglevel import Level


config = {"queue": None, "level": Level.MESSAGE}


@dataclass
class BaseContext:
    queue: list = config["queue"]
    level: int = config["level"]
    
    def execute(command: str):
        command = command.removeprefix("/")
        request_id = str(uuid4())
        
        data = json.dumps({
            "header": {
                "version": 1,
                "requestId": request_id,
                "messagePurpose": "commandRequest",
                "messageType": "commandRequest"
            },
            "body": {
                "version": 1,
                "commandLine": command,
                "origin": {
                    "type": "player"
                }
            }
        })
        
        queue.append({"data": data, "request_id": request_id})
    
    def message(message: str, target: str = "@a"):
        if level >= Level.MESSAGE:
            self.execute(f"tellraw {target} {message}")
    
    #def error

class MinecraftEventContext(BaseContext):
    def __init__(
        self,
        properties: dict,
        *base_args,
        **base_kwargs):
        super().__init__(*base_args, **base_kwargs)
        pattern = re.compile(r"(?<!^)(?=[A-Z])")
        for key, value in properties.items():
            setattr(
                self,
                pattern.sub("_", key).lower(), # convert to snake_case
                value
            )

class MessageContext(MinecraftEventContext):
    def __init__(
        self,
        properties: dict,
        *base_args,
        **base_kwargs):
        super().__init__(properties, *base_args, **base_kwargs)
    
    def reply(self, message: str):
        self.message(
            message = message,
            target = self.sender
        )