__all__ = [
    "boolean",
    "Range"
]

from functools import partial, wraps
from importlib.metadata import version as version_of
import textwrap
from typing import Optional, Sequence
from uuid import uuid4

from packaging.version import Version


shorten = partial(textwrap.shorten, width = 15)

def uuid() -> str:
    """Generate uuid v4
    
    Returns
    -------
    New random uuid v4 as string.
    """
    return str(uuid4())

def get_version() -> Version:
    """Get version of bedrockpy
    
    Returns
    -------
    Currently installed version of bedrockpy.
    """
    return Version(version_of("bedrockpy"))

def boolean(
    string: str,
    /, *,
    true: Sequence[str] = ("true", "yes"),
    false: Sequence[str] = ("false", "no")
) -> bool:
    """Converts string to boolean.
    
    Note
    ----
    Matching is case insensitive.
    
    Parameters
    ----------
    true
        Strings that indicate ``True``.
    
    false
        Strings that indicate ``False``.
    
    Returns
    -------
    ``True`` if matched one of ``true``,
    ``False`` if matched one of ``false``.
    
    Raises
    ------
    RuntimeError
        Invalid parameters are given.
    
    ValueError
        Cannot convert value to a boolean.
    """
    for x in true:
        if not isinstance(x, str):
            raise RuntimeError(f"expected 'str', got {x.__class__.__name__!r}")
        
        if x in false:
            raise RuntimeError(f"duplicate ({x!r})")
    
    if string.lower() in (i.lower() for i in true):
        return True
    
    elif string.lower() in (i.lower() for i in false):
        return False
    
    raise ValueError("string cannot be converted to boolean")

class Range:
    """
    Checks if number is withinin a specified range and returns
    the number as a float or int respectively.
    
    Attributes
    ----------
    from_
    to
    """
    def __init__(
        self,
        *,
        a: float,
        b: Optional[float] = None
    ):
        """
        Parameters
        ----------
        a
            Start value if b is defined, else end value with start at zero.
        
        b
            End value or ``None`` to use ``a`` as end value.
        """
        self.from_ = 0 if b is None else a
        self.to = a if b is None else b
    
    def __call__(self, value: float) -> int | float:
        """
        Converts ``value`` to int or float and checks if it
        is in specified range.
        
        Parameters
        ----------
        value
            A number.
        
        Returns
        -------
        The given number as int or float.
        
        Raises
        ------
        ValueError
            The number is not in range or not a number.
        """
        try:
            value = int(value)
        except ValueError:
            value = float(value)
        
        if self.from_ < value < self.to:
            return value
        
        raise ValueError(f"{value} not between {self.from_} and {self.to}")
