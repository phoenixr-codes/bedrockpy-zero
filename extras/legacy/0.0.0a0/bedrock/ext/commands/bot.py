#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
import logging
import re
from typing import Any, Callable, Coroutine, Dict, Iterable, List, Optional

from safefunc import makesafe

from bedrock.client import Client
from bedrock import docparse
from bedrock.environment import Player, Chat
from bedrock.function import Function
from bedrock.mytypes import Permission


@dataclass
class ArgumentParser:
    string: str

class MinecraftArgumentParser(ArgumentParser):
    def parse(self):
        # split command into name and arguments
        quotes = "\"'"
        pattern = f"[^{quotes} ]+|(?P<quote>[{quotes}]).*?(?P=quote)"
        # characters in quotes become one argument
        # every argument is split by any amount of spaces
        
        arguments = tuple(re.sub(
                f"^(?P<quote>[{quotes}])(?P<content>.*?)(?P=quote)$", # remove quotes if exist
                lambda m: m.group("content"),
                m.group()
        ) for m in re.finditer(pattern, command_message))
        
        # return command_name & command_args
        return arguments

'''
class TerminalArgumentParser(ArgumentParser):
    def parse(self):
        quotes = "\"'"
        pattern f"(-(?P<key>[^{quotes} ]))|(--(?P<key>[^{quotes} ]+)) (?P<value>"


class PythonArgumentParser(ArgumentParser):
    
'''


@dataclass
class RootReference:
    path: Iterable
    
    def __str__(self):
        text = ""
        for i in path:
            text += f"[{path!r}]"
        return text
    
    def access(self, dictionary: dict):
        value = dictionary
        for i in path:
            value = value[i]
        return value


@dataclass
class Command:
    name: str
    coro: Coroutine = field(repr = False)
    enabled: bool = field(repr = False)
    aliases: List[str] = field(repr = False)
    permission: Permission = field(repr = False)
    summary: Optional[str]
    description: Optional[str] = field(repr = False)
    usage: Optional[str] = field(repr = False)
    parameters: dict = field(repr = False)
    
    def __post_init__(self):
        params = Function(self.coro).params
        syntax = self.name
        for param in params:
            content = f"{param.name}: {param.annotation}"
            if param.optional:
                syntax += f" [{content}]"
            else:
                syntax += f" <{content}>"
        self.syntax = syntax
        
        self.error_handler = lambda ctx, error: ctx.error(error)
    
    def __str__(self):
        return self.syntax
    
    def __bool__(self):
        return self.enabled
    
    def error(self, coro: Callable) -> Callable:
        self.error_handler = coro
        return coro
    
    async def __call__(self, *args, **kwargs):
        return await self.coro(*args, **kwargs)



class Bot(Client):
    def __init__(
        self,
        command_prefix: str,
        command_style = MinecraftArgumentParser,
        *client_args: Any,
        **client_kwargs: Any
    ):
        super().__init__(*client_args, **client_kwargs)
        self.command_prefix = command_prefix
        self.command_handler = {}
        
        async def player_message(ctx, message, author):
            command_message = message.removeprefix(self.command_prefix)
            if command_message != message:
                # split command into name and arguments
                quotes = "\"'"
                pattern = f"[^{quotes} ]+|(?P<quote>[{quotes}]).*?(?P=quote)"
                # characters in quotes become one argument
                # every argument is split by any amount of spaces
                
                arguments = tuple(
                    re.sub(
                        f"^(?P<quote>[{quotes}])(?P<content>.*?)(?P=quote)$", # remove quotes if exist
                        lambda m: m.group("content"),
                        m.group()
                    ) for m in re.finditer(pattern, command_message)
                )
                command_name, *command_args = arguments
                
                command = self.command_handler.get(command_name)
                if command is not None:
                    if command is RootReference:
                        command = command.access(self.command_handler)
                    if command:
                        if self.authorized(author, command.permission):
                            
                            param_len = range(
                                len([
                                    1 for p in command.parameters if not p.optional
                                ]),
                                len(list(
                                    command.parameters
                                ))
                            )
                            given_len = len(command_args)
                            diff = abs(param_len - given_len)
                            
                            if given_len < min(param_len):
                                missing = [p.name for p in commands]
                                logging.warning(f"Missing arguments: {command.params[diff:]}")
                            elif given_len > max(param_len):
                                logging.warning(f"Too many arguments: {command_args[diff:]}")
                            else:
                                result = await command(context, *command_args)
                                if not result.success:
                                    logging.warning(f"{result}")
                        
                        else:
                            logging.warning(f"{author} is not authorized to execute {command_name}")
                    else:
                        logging.warning(f"{author} tried to execute disabled command: {command_name}")
        
        self._add_any_event(
            handler = self.minecraft_event_handler,
            position = 1,
            coro = player_message
        )
    
    def command(
        self,
        name: Optional[str] = None, # default: function name
        aliases: List[str] = [],
        permission: Permission = set(), # this option includes self.owners
        enabled: bool = True,
        
        chat: int = Chat.BOTH,
        
        summary: Optional[str] = None,
        description: Optional[str] = None,
        usage: Optional[Dict[str, str]] = None
    ):
        permission.update(self.owners)
        def decorator(command_function):
            command_name = command_function.__name__ or name
            
            if command_name in self.command_handler:
                raise DuplicateError(command_name)
            
            doc = docparse.BedrockDocString(command_function.__doc__ or "")
            
            self.command_handler[command_name] = Command(
                name =        command_name,
                coro =        makesafe(return_entire_result = True)(command_function),
                enabled =     enabled,
                aliases =     aliases,
                permission =  permission,
                summary =     summary     or doc.get("Summary"),
                description = description or doc.get("Description"),
                usage =       usage       or doc.get("Usage"),
                parameters =  Function(command_function).params,
            )
            
            for alias in aliases:
                if alias in self.command_handler:
                    raise DuplicateError(alias)
                
                # We won't take the same value as in the main name
                # because in case the value gets changed, then the
                # value won't get updated for the aliases.
                # We instead refer to the directory to the main name.
                self.command_handler[alias] = RootReference(command_name)
            
        return decorator
    
    