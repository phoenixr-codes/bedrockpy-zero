import inspect
import re
import shlex
import sys
import types
import typing

from . import ui
from .context import Context


ErrorHandler = typing.Callable[[Context, Exception], None]


class CommandError(Exception):
    """Base Exception for errors raised due to processing commands"""
    def describe(self):
        return f"{self.__class__.__name__}: {str(self)}"

class BadArgumentError(CommandError):
    pass

class MissingArgumentsError(CommandError):
    pass

class TooManyArgumentsError(CommandError):
    pass

class UnknownCommandError(CommandError):
    pass

class MissingQuoteError(CommandError):
    pass


QUOTES = "\"'"

def _isunion(x: typing.Any, /):
    if sys.version_info[:2] >= (3, 10):
        if isinstance(x, types.UnionType):
            return True
    
    return type(x) == typing._UnionGenericAlias

def get_command_args(string: str) -> list[str]:
    """Split command arguments.
    
    Characters in quotes become one argument
    every argument is split by any amount of spaces.
    
    Parameters
    ----------
    string
        Server command without prefix.
    
    Returns
    -------
    List of command name along with all arguments.
    """
    
    pattern_splitargs = re.compile(f"[^{QUOTES} ]+|(?P<quote>[{QUOTES}]).*?(?P=quote)")
    pattern_removequotes = re.compile(f"^(?P<quote>[{QUOTES}])(?P<content>.*?)(?P=quote)$")
    
    # return (command_name, command_arg1, ...)
    return [
        pattern_removequotes.sub(
            lambda m: m.group("content"),
            m.group()
        ) for m in re.finditer(pattern_splitargs, string)
    ]

def get_command_args_v2(string: str) -> list[str]:
    """Split command arguments.
    
    Like :func:`get_command_args` but raise error
    when closing quote is missing.
    
    Raises
    ------
    :class:`MissingQuoteError`
    
    """
    try:
        return shlex.split(string)
    except ValueError:
        raise MissingQuoteError("missing closing quote")


def convert_args(
    given_args: typing.Sequence[str],
    command_function: typing.Callable
) -> typing.Generator[typing.Any, None, None]:
    """Convert arguments by the commands' specified type annotations.
    
    Parameters
    ----------
    given_args
        Server command arguments to convert.
    
    command_function
        Function of the command.
    
    Yields
    ------
    :class:`typing.Any`
        Converted arguments.
    
    Raises
    ------
    :class:`TooManyArgumentsError`
    :class:`BadArgumentError`
    :class:`MissingArgumentsError`
    
    """
    sig = inspect.signature(command_function)
    params = sig.parameters
    params = list(params.values())
    
    idx = 1 # first argument is ctx, so we skip that
    # we're not using enumerate because for the case
    # given_args is empty we can access it below the
    # loop
    
    for arg in given_args:
        try:
            param = params[idx]
        except IndexError:
            raise TooManyArgumentsError(f"command takes {len(params) - 1} arguments but {len(given_args)} were given")
        
        # special converters
        if _isunion(param.annotation):
            converters = param.annotation.__args__
            for converter in converters:
                try:
                    yield converter(arg)
                
                except ValueError:
                    pass
                
                else:
                    break
            
            else:
                raise BadArgumentError(f"could not convert {arg!r} to one of {converters}")
        
        # basic converters
        else:
            converter = str if param.annotation is inspect.Parameter.empty else param.annotation
            try:
                yield converter(arg)
            except ValueError:
                raise BadArgumentError(f"could not convert {arg!r} to {param.annotation.__name__!r}")
        
        idx += 1
    
    # check if parameters without default value are covered
    left_params = params[idx + 1:]
    for param in left_params:
        if param.default is inspect.Parameter.empty:
            raise MissingArgumentsError(f"argument {param.name} is missing")

class Command:
    """
    Attributes
    ----------
    name
        Name of the command.
    
    function
        Command function.
    
    aliases
        Alternative names of the command.
    
    enabled
    
    description
    
    help
    
    error_handlers
        .. seealso:: :meth:`error`
    
    """
    def __init__(
        self,
        function: typing.Callable,
        name: typing.Optional[str] = None,
        *,
        aliases: list[str] = [],
        enabled: bool = True,
        description: str = "",
        help: str = "",
    ):
        """
        Parameters
        ----------
        function
            Command function.
        
        name
            Name of the command.
        
        aliases
            Alternative names of the command.
        
        enabled
        description
        help
        
        """
        self.name = name or function.__name__
        self.function = function
        self.aliases = aliases
        self.enabled = enabled
        self.description = description
        self.help = help
        self.error_handlers: dict[Exception, ErrorHandler] = {}
    
    def __repr__(self):
        return f"Command({self.name!r})"
    
    def __str__(self) -> str:
        return self.name
    
    def __bool__(self) -> bool:
        return self.enabled
    
    def get_names(self) -> typing.Generator[str, None, None]:
        """
        Yields
        ------
        All names the command can be triggered with.
        """
        yield self.name
        yield from self.aliases
    
    def error(self, *exceptions: Exception):
        """Catches exceptions raised while running a command.
        
        Parameters
        ----------
        exceptions
            :class:`Exception`\s the server should catch.
        
        Example
        -------
        Send an error message if player tried to
        divide through zero::
           
           @app.command()
           async def divide(ctx, a: float, b: float):
               await ctx.reply(f"{a / b = }")
        
           @divide.error(ZeroDivisionError)
           async def catch(ctx, exc):
               await ctx.reply("cannot divide through zero")
        
        """
        def wrapper(function: ErrorHandler):
            for exc in exceptions:
                self.error_handlers[exc] = function
            
            return function
        return wrapper
    
    async def __call__(self, *args, **kwargs):
        return await self.function(*args, **kwargs)

class CommandGroup:
    pass

