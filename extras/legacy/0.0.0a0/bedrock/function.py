#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inspect
from typing import Any, Callable


class NULL:
    def __repr__(self):
        return "<NULL>"
    
    def __str__(self):
        return "null"

def to_null(x: Any) -> Any:
    if x is inspect.Parameter.empty:
        return NULL()
    return x

class Function:
    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        self.doc = inspect.cleandoc(func.__doc__ or "")
        self.params = []
        
        params = tuple(inspect.signature(func).parameters.values())
        for param in params:
            self.params.append(Parameter(
                name = param.name,
                annotation = to_null(param.annotation),
                default = to_null(param.default),
                is_args = param.kind == inspect.Parameter.VAR_POSITIONAL,
                is_kwargs = param.kind == inspect.Parameter.VAR_KEYWORD
            ))
    
    def __repr__(self):
        return self.name + "(" + ",".join(map(str, self.params)) + ")"
    
    def __str__(self):
        return self.name
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class Parameter:
    def __init__(
        self,
        name: str,
        annotation: Any,
        default: Any,
        is_args: bool,
        is_kwargs: bool
    ):
        self.name = name
        self.annotation = annotation
        self.default = default
        self.is_args = is_args
        self.is_kwargs = is_kwargs
        self.optional = is_args or is_kwargs or (default is not NULL)
    
    def __str__(self):
        return self.name + (
            f":{self.annotation.__name__}" if self.annotation is not NULL else ""
        ) + (
            f"={self.default!r}" if self.default is not NULL else ""
        )

if __name__ == '__main__':
    from typing import Optional
    
    def div(a: float, b: float = 2) -> Optional[float]:
        """
        Hello World
        """
        if b == 0.:
            return None
        return a / b
    
    func = Function(div)
    print(f"{func = }")
    print(f"{func.name = }")
    print(f"{func.doc = }")
    
    params = func.params
    for param in params:
        print(f"{param = !s}")
        print(f"{param.name = }")
        print(f"{param.annotation = }")
        print(f"{param.default = !r}")
        print(f"{param.is_args = }")
        print(f"{param.is_kwargs = }")
        print(f"{param.optional = }")
