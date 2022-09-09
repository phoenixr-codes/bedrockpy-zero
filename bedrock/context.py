"""
Contexts are used in most server events and commands.
They contain the data of events you have subscribed
to. They allow you to react on these events.
"""

import json
import typing

from . import ui

class Context:
    """
    Attributes
    ----------
    data
        The data that the server received by Minecraft
        that matches the context.
    """
    def __init__(self, server: 'Server', **data: dict[str, typing.Any]):
        self._server = server
        self.data = data
    
    async def run(self, command: str) -> None:
        """Executes a Minecraft command.
        
        Parameters
        ----------
        command
            The Minecraft command to execute. The
            leading slash may be omitted.
        """
        await self._server.command_request(command)
    
    async def tell(self, text: str, target: str = "@a") -> None:
        """
        Parameters
        ----------
        text
            The message to display.
        
        target
            A target selector. See the
            :doc:`reference <minecraft-references>`
            for more information.
        """
        await self.run(f"tell {target} {text}")
    
    async def tell_raw(self, text, target: str = "@a") -> None:
        """Like :meth:`tell` but without seeing that the server sent the message.
        """
        data = json.dumps({
            "rawtext": [{
                "text": text
            }]
        })
        await self.run(f"tellraw {target} {data}")
    
    async def tell_error(self, text: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Display a message as error.
        
        This method is a wrapper around :meth:`tell_raw` that
        formats the text to an error looking message.
        """
        await ctx.tell_raw(ui.red(text), *args, **kwargs)


class Message(Context):
    """
    .. note::
       
       More attributes can be accessed by the
       ``data`` attribute.
    
    Attributes
    ----------
    message
    receiver
    author
    chat_type
    """
    def __init__(self, server: 'Server', **data: dict[str, typing.Any]):
        super().__init__(server, **data)
        
        # expecting body in data
        self.message = data["message"]
        self.receiver = data["receiver"]
        self.author = data["sender"]
        self.chat_type = data["type"]
    
    async def reply(self, *args: typing.Any, **kwargs: typing.Any):
        """Like :meth:`tell` but send a private message to the target.
        """
        await self.tell(
            *args, **kwargs,
            target = self.author,
        )
    
    async def reply_raw(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Like :meth:`tell_raw` but send a private message to the target.
        """
        await self.tell_raw(
            *args, **kwargs,
            target = self.author
        )
    
    async def reply_error(self, text: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Like :meth:`tell_error` but send a private message to the target.
        """
        await ctx.reply_error(
            text,
            *args, **kwargs,
            target = self.author
        )
