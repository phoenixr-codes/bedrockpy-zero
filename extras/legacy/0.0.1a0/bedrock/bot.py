from dataclasses import dataclass, field
import time
import typing

from bedrock import Client


def uncallable():
    raise RuntimeError("coroutines added to the bot cannot be called")

@dataclass
class Command:
    # TODO: order
    name: str
    aliases: list = field(default_factory = list, repr = False)
    coroutine: typing.Awaitable = field(repr = False)
    created_at: float = field(default_factory = time.now, repr = False)
    brief: str = ""
    description: str = field(default = "", repr = False)
    enabled: bool = True
    hidden: bool = field(default = False, repr = False)
    
    async def __call__(*args):
        await self.coroutine(..., *args)

class HelpCommand(Command):
    def __new__(self):
        ...

class Bot(Client):
    def __init__(
        self,
        command_prefix: str,
        help_command: HelpCommand = HelpCommand()
    ):
        ...
    
    def add_command(self, *args, **kwargs):
        self.Command(*args, **kwargs)
    
    def command(self, coroutine: Awaitable):
        def wrapper(*args, **kwargs):
            self.add_command(coroutine, *args, **kwargs)
        return wrapper()
    
    async def process_command(self, message):
        ...
    
    async def on_message(self, message: Message):
        await process_command(message)