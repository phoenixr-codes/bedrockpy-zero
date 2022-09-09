from __future__ import annotations

__all__ = ["Server"]

import asyncio
from dataclasses import dataclass
from datetime import datetime
import difflib
from functools import partial
import inspect
import json
import logging
from pathlib import Path
from socket import gethostbyname
import sys
import typing

from convert_case import pascal_case
from ruamel.yaml import YAML
from websockets import server
from websockets.exceptions import ConnectionClosedError

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from . import commands, context, debug_interface
from .command_parsers import CommandParser
from .utils import uuid, shorten


WebsocketData = dict[str, dict[str, typing.Any]]
Handler = typing.Callable
HandlerContainer = dict[str, Handler]


logger = logging.getLogger(__name__)
yaml = YAML()


MAX_COMMAND_PROCESSING = 100


@dataclass
class CommandRequest:
    id: str
    data: WebsocketData

def log(websocket_data: WebsocketData, logpath: Path = Path.cwd() / "log"):
    if logger.isEnabledFor(logging.DEBUG):
        logpath.mkdir(exist_ok = True)
        time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with (logpath / f"{time}.log.yaml").open("w") as f:
            yaml.dump(websocket_data, f)


class Server:
    def __init__(
        self,
        host: str,
        port: int,
        *,
        command_prefix: typing.Optional[str] = None,
        command_parser: typing.Optional[CommandParser] = None,
        command_args_parser: typing.Callable[[str], list[str]] = commands.get_command_args_v2,
        loop: typing.Optional[asyncio.AbstractEventLoop] = None,
        debug: bool = False,
    ):
        """
        Parameters
        ----------
        host
            The host where the server is going to run.
        
        port
            The port where the server is going to run.
        
        command_prefix
            A string which every command but be prefixed
            with. May be set to ``None`` if no commands
            are being used.
        
        command_parser
            A :class:`CommandParser` defining its own
            parsing rules. Cannot be used with normal
            commands.
        
        command_args_parser
            Takes a string (message of player) and returns
            a list of arguments.
        
        loop
            The asyncio event loop to use. Defaults to ``asyncio.get_event_loop``.
        
        debug
            Enable debug mode.
        """
        if command_parser is not None and command_prefix is None:
            raise ValueError("specify `command_prefix` as well when using `command_parser`")
        
        self._host = gethostbyname(host)
        self._port = port
        
        self.debug = debug
        
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        
        self.ws = None
        
        self.command_args_parser = command_args_parser
        
        self.command_prefix = command_prefix
        self.command_parser = command_parser
        
        
        self._prefix = "on_"
        
        self._event_handlers: HandlerContainer  = {}
        self._minecraftevent_handlers: HandlerContainer = {}
        self._commands: list[commands.Command] = []
        
        self._commands_pending: list[dict] = [] # command request that are going to be sent as soon as `_commands_sent` has enough space (100)
        self._commands_sent: list[dict] = [] # command requests that got sent and will be dropped as soon as Minecraft proceeded them
        # https://www.s-anand.net/blog/programming-minecraft-with-websockets/#wait-for-commands-to-be-done
        
        
        if command_parser is not None:
            async def _(**_):
                pass
            
            self._minecraftevent_handlers["PlayerMessage"] = _
    
    
    async def __aenter__(self):
        self.start()
        return self
    
    async def __aexit__(self, *exc):
        self.stop()
    
    async def _update_queue(self):
        request = self._commands_pending.pop(0)
        await self.send(request.data)
        self._commands_sent.append(request.id)
    
    def _remove_prefix(self, string: str) -> str:
        output = string.removeprefix(self._prefix)
        if len(output) != len(string):
            raise ValueError(f"missing prefix {self._prefix!r}")
        return output
    
    
    #:=================
    # Events & Commands
    #:=================
    
    def add_event(self: T, handler: Handler) -> T:
        self._event_handlers[self._remove_prefix(handler.__name__)] = handler
        return self
    
    def remove_event(self: T, handler: Handler) -> T:
        for k, v in self._event_handlers.items():
            if v == handler:
                del self._event_handlers[k]
        return self
    
    def add_minecraftevent(self: T, handler: Handler) -> T:
        self._minecraftevent_handlers[pascal_case(handler.__name__)] = handler
        return self
    
    def remove_minecraftevent(self: T, handler: Handler) -> T:
        for k, v in self._minecraftevent_handlers.items():
            if v == handler:
                del self._minecraftevent_handlers[k]
        return self
    
    def add_command(self: T, command: commands.Command) -> T:
        if self.command_parser is not None:
            raise ValueError("you already set a custom command parser")
        
        if self.command_prefix is None:
            raise ValueError("please set a command prefix")
        
        if (event := "PlayerMessage") not in self._minecraftevent_handlers:
            async def _(**_):
                pass
            
            self._minecraftevent_handlers[event] = _
        
        for registered_command in self._commands:
            registered_names = registered_command.get_names()
            for name in command.get_names():
                if any(whitespace in name for whitespace in [" \t\n\r\f\v"]):
                    raise ValueError(f"command must not contain whitespaces ({name!r})")
                
                if name in registered_names:
                    raise ValueError(f"command with name or alias {name} is already registered")
        
        self._commands.append(command)
        return self
    
    def remove_command(self: T, command: commands.Command) -> T:
        for k, v in self._commands.items():
            if v == command:
                del self._commands[k]
        return self
    
    def event(self, handler: Handler) -> Handler:
        """
        Example usage::
        
            @app.event
            async def on_connect(ctx):
                ctx.msg("Hello World")
        
        """
        self.add_event(handler)
        return handler
    
    def minecraftevent(self, handler: Handler) -> Handler:
        """
        Example usage::
        
            @server.minecraftevent
            async def end_of_day(ctx):
                ctx.msg("And there the day ends!")
        
        """
        self.add_minecraftevent(handler)
        return handler
    
    def command(self, *args, **kwargs):
        """
        Example usage::
        
            @server.command()
            async def ping(ctx, message = "Pong!"):
                ctx.msg(message)
        """
        def wrapper(function_or_class):
            if inspect.isclass(function_or_class):
                raise NotImplementedError()
                
            elif inspect.iscoroutinefunction(function_or_class):
                command = commands.Command(*args, **kwargs, function = function_or_class)
                self.add_command(command)
                return command
            
            else:
                raise ValueError(
                    f"cannot use {function_or_class.__name__!r} as command; "
                    "must be a class or coroutine function"
                )
        return wrapper
    
    
    #:==============
    # Websocket Data
    #:==============
    
    async def send(self, data: WebsocketData) -> None:
        """Wrapper for sending data to the Minecraft client
        
        Normally, there is no need for you to
        use this method manually.
        
        Note
        ----
        ``data`` should follow a format like this::
            
            {
                "header": {
                    "version": 1,
                    "requestId": uuid(),
                    "messageType": ...,
                    "messagePurpose": ...
                },
                "body": ...
            }
        
        Parameters
        ----------
        data
        
        """
        assert self.ws is not None, "connection not established yet"
        await self.ws.send(json.dumps(data))
    
    async def subscribe(self, event_name: str):
        """Wrapper for subscribing to a Minecraft event
        
        Normally, there is no need for you to
        use this method manually.
        
        Parameters
        ----------
        event_name
        
        """
        await self.send({
            "header": {
                "version": 1,
                "requestId": uuid(),
                "messageType": "commandRequest",
                "messagePurpose": "subscribe"
            },
            "body": {
                "eventName": event_name
            }
        })
    
    async def unsubscribe(self, event_name: str):
        """Wrapper for unsubscribing to a Minecraft event
        
        Normally, there is no need for you to
        use this method manually.
        
        Parameters
        ----------
        event_name
        
        """
        await self.send({
            "header": {
                "version": 1,
                "requestId": uuid(),
                "messageType": "commandRequest",
                "messagePurpose": "unsubscribe"
            },
            "body": {
                "eventName": event_name
            }
        })
    
    async def command_request(self, command: str) -> None:
        """Wrapper for subscribing to a Minecraft event
        
        Normally, there is no need for you to
        use this method manually but rather call
        the :meth:`run` method on a :class:`Context`
        object.
        
        Parameters
        ----------
        command
            The Minecraft command, the server will execute.
            The ``/`` prefix can be omitted.
        
        """
        command = command.removeprefix("/")
        command_id = uuid()
        
        data = {
            "header": {
                "version": 1,
                "requestId": command_id,
                "messageType": "commandRequest",
                "messagePurpose": "commandRequest"
            },
            "body": {
                "version": 1,
                "commandLine": command,
                "origin": {
                    "type": "player"
                }
            }
        }
        
        self._commands_pending.append(CommandRequest(command_id, data))
        if len(self._commands_sent) < MAX_COMMAND_PROCESSING:
            await self._update_queue()
    
    
    #:==========
    # Connection
    #:==========
    
    @staticmethod
    def on_error(exc: Exception, function: typing.Callable) -> None:
        logger.exception(
            f"encountered error while executing {function.__name__!r}: "
            f"the exception {str(exc)!r} will be ignored"
        )
    
    async def _command_error(
        self,
        *,
        command: typing.Optional[commands.Command] = None,
        exc: Exception,
        ctx: context.Context
    ):
        if command is not None and any(issubclass(exc.__class__, err) for err in command.error_handlers):
            for err in command.error_handlers:
                if issubclass(exc.__class__, err):
                    await command.error_handlers[err](ctx, exc)
                    if self.debug:
                        await ctx.reply_error(f"[Debugger] {command.function.__name__!r} raised {exc!r}")
        
        elif isinstance(exc, commands.CommandError):
            await ctx.reply_error(exc.describe())
        
        else:
            self.on_error(exc, command.function)
    
    async def _process_message(self, data: WebsocketData):
        log(data)
        
        header = data["header"]
        body = data["body"]
        isresponse = header.get("messagePurpose") == "commandResponse"
        
        event = header.get("eventName")
        
        handler = self._minecraftevent_handlers.get(event)
        if handler:
            await handler(**body)
        
        if isresponse:
            # check if pending request has been
            # answered with this message
            request_id = header["requestId"]
            self._commands_sent.remove(request_id)
            if self._commands_pending:
                await self._update_queue()
            
        if event != "PlayerMessage":
            return
        
        ctx = context.Message(self, **body)
        
        # check if message is a command
        if not all((
            self.command_prefix,
            ctx.message.startswith(self.command_prefix),
            ctx.message != self.command_prefix
        )):
            return
        
        cmdstr = ctx.message.removeprefix(self.command_prefix)
        
        if self.command_parser is not None:
            try:
                await self.command_parser.parse(ctx, cmdstr)
            except Exception as exc:
                exception = commands.CommandError(str(exc))
                await self._command_error(
                    exc = exception,
                    ctx = ctx
                )
        
        else:
            try:
                name, *args = self.command_args_parser(cmdstr)
            except commands.MissingQuoteError as exc:
                await self._command_error(
                    exc = exc,
                    ctx = ctx
                )
                return
            
            for cmd in self._commands:
                if name not in (cmd.name, *cmd.aliases):
                    continue
                
                # convert arguments
                try:
                    converted_args = commands.convert_args(args, cmd.function)
                
                except Exception as exc:
                    await self._command_error(
                        command = cmd,
                        exc = exc,
                        ctx = ctx
                    )
                
                # pass arguments
                try:
                    await cmd(ctx, *converted_args)
               
                except Exception as exc:
                    await self._command_error(
                        command = cmd,
                        exc = exc,
                        ctx = ctx
                    )
                
                return
            
            
            # command not found
            registered_names = []
            
            for command in self._commands:
                registered_names.extend(command.get_names())
            
            close_match = difflib.get_close_matches(name, registered_names)
            
            if not close_match:
                suffix = ""
            
            elif len(close_match) == 1:
                suffix = f"; perhaps you meant {close_match[0]!r}?"
            
            else:
                suffix = f"; perhaps you meant one of {', '.join(map(repr, close_match))}?"
            
            await self._command_error(
                exc = commands.UnknownCommandError(f"command {name!r} does not exist{suffix}"),
                ctx = ctx
            )
    
    async def _handler(self, ws):
        self.ws = ws
        logger.info("Connection established")
        
        for event_name in self._minecraftevent_handlers:
            logger.debug(f"Subscribing to {event_name} ...")
            await self.subscribe(event_name)
        
        if self.debug:
            ctx = context.Context(self)
            
            await ctx.tell_raw(
                debug_interface.WELCOME1,
                target = "@a",
            )
            
            await ctx.tell_raw(
                debug_interface.WELCOME2
                % {"host": self._host, "port": self._port},
                target = "@a",
            )
        
        try:
            async for message in ws:
                logger.info(f"Received data {shorten(message)}")
                data = json.loads(message)
                
                await self._process_message(data)
        
        except ConnectionClosedError as exc:
            if (event := self._event_handlers.get("disconnect")):
                await event(context.Context(self))
            
            await self.wait_closed()
    
    def run(self, **ws_options: typing.Any):
        ws = server.serve(
            self._handler,
            **ws_options,
            host = self._host,
            port = self._port,
        )
        
        logger.info(f"Ready @ {self._host}:{self._port}")
        
        self.loop.run_until_complete(ws)
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.loop.stop()
        
    def close(self):
        logger.debug("closing server ...")
        self.ws.stop()
        self.loop.stop()
    
    async def wait_closed(self):
        logger.debug("closing server ...")
        await self.ws.wait_closed()
        self.loop.stop()
        logger.info("closed ...")
        
