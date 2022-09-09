#!/usr/bin/env python3
# -*- coding: utf-8 -*-

############################################
# Notes / ToDo

# - allow multiple event functions (declare
#   order with queue argument)
# - command style (minecraft, terminal, normal)


############################################
# Future Projects

# [ ] WorldEdit
# [✓] Pixel Art


############################################
# Code

import asyncio
import io
import json
import logging
import sys
import time
import traceback
from typing import Any, Awaitable, Callable, Coroutine, Dict, Iterator, List, Optional
from uuid import uuid4

from convert_case import snake_case
from safefunc import makesafe
import websockets
from websockets.exceptions import ConnectionClosedError

from . import context
from .environment import ANY_PLAYER, Permission, Player
from .exceptions import DuplicateError
from .msglevel import Level
from .mytypes import Handler, Host, Port


# Logging

log_root = logging.getLogger(__name__)
log_session = logging.getLogger(__name__)
log_mc = logging.getLogger(__name__)

log_session.addHandler(logging.FileHandler("session.log"))
log_mc.addHandler(logging.StreamHandler(io.StringIO()))

class WSLoggerAdapter(logging.LoggerAdapter):
    """Add connection ID and client IP address to websockets logs."""
    # we configure the logging for websockets further down in Client.start()
    def process(self, msg, kwargs):
        try:
            websocket = kwargs["extra"]["websocket"]
        except KeyError:
            return msg, kwargs
        xff = websocket.request_headers.get("X-Forwarded-For")
        return f"{websocket.id} {xff} {msg}", kwargs


# Contants

COMMAND_REQUEST_LIMIT = 100
# 'command' does not mean ingame commands like
# /say or /setblock, it rather means any request
# you send to Minecraft. 


def formattime(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(seconds, 60)
    days, hours = divmod(hours, 24)
    return (days, hours, minutes, seconds)

def prefered_name(name: str, alternative: Optional[str]):
    return snake_case(name) if alternative is None else alternative

iscoro = asyncio.iscoroutinefunction


class Client:
    def __init__(
        self,
        name: Optional[str] = None,
        owners: Permission = Permission(),
        level: int = Level.MESSAGE,
        loop = asyncio.get_event_loop()
    ):
        # Metadata
        self.name = name
        self.owners = owners
        self.level = level
        self.loop = loop
        self.ws = None
        
        self.started = -1.
        # the time where the bot got started will be assigned 
        # as soon as a connection has been established
        
        self.event_prefix = "on_"
        self.minecraft_event_prefix = ""
        
        # Handlers
        self.event_handler = {}
        self.minecraft_event_handler = {}
        
        # Connection
        self.send_queue = [] # requests that need to be executed
        self.awaited_queue = {} # requests that got sent, but didn't got a response
        # After 100 pending requests the bot
        # waits until one requests has been
        # processed.
        # If you still try to send a request,
        # Minecraft will send an error.
    
    async def sleep(duration: float) -> None:
        await asyncio.sleep(duration)
    
    def authorized(
        self,
        player: Player,
        permission: Optional[Permission] = None
    ):
        permission = permission or self.owners
        return player in permission
    
    def latency(
        self
    ):
        pass
    
    @staticmethod
    def _add_any_event(
        handler: Handler,
        coro: Coroutine,
        prefix: str = "",
        position: int = 0,
        name: Optional[str] = None,
        **kwargs
    ):
        coroname = coro.__name__.removeprefix(prefix)
        name = prefered_name(coroname, name)
        
        if name in handler:
            raise DuplicateError(name)
        
        content = handler.get(name)
        if content is None:
            handler[name] = [None, None]
        handler[name][position] = kwargs | {"coro": coro}
        logging.info("Event has been added")
    
    def event(
        self,
        enabled: bool = True
    ):
        def decorator(coro):
            self._add_any_event(
                handler = self.event_handler,
                prefix = self.event_prefix,
                coro = coro,
                
                enabled = enabled
            )
        
        return decorator
    
    def minecraft_event(
        self,
        enabled: bool = True
    ):
        def decorator(coro):
            self._add_any_event(
                handler = self.minecraft_event_handler,
                prefix = self.minecraft_event_prefix,
                coro = coro,
                
                enabled = enabled
            )
        
        return decorator
    
    async def run_event(
        self,
        name: str,
        handler: Optional[Handler] = None,
        args: Iterator = (),
        kwargs: dict = {}
    ) -> None:
        if handler is None:
            handler = self.event_handler
        if name in handler:
            for event in handler[name]:
                if event is not None:
                    result = await event["coro"](*args, **kwargs)
                    success = bool(result)
    
    async def close(self):
        await self.ws.close()
        self.ended = time.time()
        seconds = self.ended - self.started
        dd, hh, mm, ss = formattime(seconds)
        log_session.info(f"Bot is closed. Run [{hh}:{mm}:{ss}]")
        return (dd, hh, mm, ss)
    
    def run(
        self,
        host: Host,
        port: Port
    ):
        async def handler(ws):
            log_root.debug(f"{type(ws) = }")
            
            self.ws = ws
            self.started = time.time()
            
            context.config = {
                "queue": self.send_queue,
                "level": self.level
            }
            
            await self.run_event(
                "connect"
            )
            
            # Minecraft will only send data for specific events
            # the client subscribed to
            # We loop through every event that was registered
            # with the 'minecraft_event' decorator.
            for minecraft_event in self.minecraft_event_handler:
                # Because Minecraft has its events in pascalcase
                # and python prefers snakecase, we convert the
                # snakecase event name into pascalcase
                event_name = minecraft_event.replace("_", " ").title().replace(" ", "")
                
                data = json.dumps({
                    "header": {
                        "version": 1,
                        "requestId": str(uuid4()),
                        "messageType": "commandRequest",
                        "messagePurpose": "subscribe"
                    },
                    "body": {
                        "eventName": event_name
                    }
                })
                
                # It's okay to not queue these requests because
                # there are never going to be more than 100 event
                # requests.
                await ws.send(data)
            
            try:
                async for data in ws:
                    data = json.loads(data)
                    log_mc.debug(f"{data}")
                    
                    header = data["header"]
                    body = data["body"]
                    properties = body["properties"]
                    
                    event = body.get("eventName")
                    
                    if event is not None:
                        event = snake_case(event)
                        args = ()
                        
                        if event == "player_message":
                            ctx = context.MessageContext(properties)
                            args = (
                                ctx,
                                ctx.message,
                                ctx.sender
                            )
                        
                        
                        
                        await self.run_event(
                            name = event,
                            handler = self.minecraft_event_handler,
                            args = args
                        )
                    
            except ConnectionClosedError as exc:
                await self.run_event(
                    "disconnect",
                    exc.rcvd or exc.sent
                )
                await self.close()
        
        launch = websockets.serve(
            handler,
            host = host,
            port = port,
            #logging = WSLoggerAdapter(logging.getLogger("websockets.server"))
        )
        
        # because the 'ready' event is not async
        # we won't use the run_event function
        if (evt := "ready") in self.event_handler:
            self.event_handler[evt][0]["coro"](host = host, port = port)
        
        self.loop.run_until_complete(launch)
        self.loop.run_forever()