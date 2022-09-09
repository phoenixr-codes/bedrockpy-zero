*************
Command Guide
*************

This is a detailed guide on how to create
commands in bedrockpy.

.. code-block:: python3
    
    import bedrock
    
    app = bedrock.Server(
        "localhost", 6464,
        command_prefix = "$"
    )
    
    @app.command()
    async def echo(ctx):
        """says something nice"""
        ctx.tell("Hello there!")

This will print ``Hello there!`` to the Minecraft
Chat when someone types ``$echo``.


===================
Specifing Arguments
===================

.. code-block:: python3
    
    @app.command()
    async def echo(ctx, message: str):
        """says something nice"""
        ctx.tell(message)

This requires the player to include a message
as an argument. We may also define a default
value so that argument can be omitted.

.. code-block:: python3
    
    @app.command()
    async def echo(ctx, message: str = "Hello there!"):
        """says something nice"""
        ctx.tell(message)


==========
Converters
==========

-------------------
Usage of converters
-------------------

The previously used type hint ``str`` can be
omitted. If we however specify another type
hint such as ``int`` or ``float`` the server
will convert it respectively.

.. code-block:: python3
    
    @app.command()
    async def add(ctx, a: int, b: int):
        """adds two integers"""
        ctx.tell(a + b)

You may use any callable that takes one
string as an argument.


-------------------------
The problem with ``bool``
-------------------------

The built-in ``bool`` function returns whether
a string contains characters or not. In the
context of commands we want to determine if
a string means ``True`` or ``False``. We cannot
achieve this with the ``bool`` function. There
is however a function defined in the bedrockpy
library named ``boolean``.

.. code-block:: python3
    
    from bedrock.utils import boolean
    
    @app.command()
    async def echo(ctx, uppercase: boolean = False):
        """says somerhing nice"""
        msg = "Hello there!"
        if uppercase:
            msg = msg.upper()
        ctx.tell(msg)

By default ``true`` and ``yes`` will match ``True``
and ``false`` and ``no`` will match ``False``. We can
also redefine these values. Note that the conversion
is case insensitive.

.. code-block:: python3
    
    from functools import partial
    from bedrock.utils import boolean as orig_boolean
    
    boolean = partial(
        orig_boolean,
        true = ["true", "yes", "1", "on"],
        false = ["false", "no", "0", "off"]
    )
    
    @app.command()
    async def echo(ctx, uppercase: boolean = False):
        """says somerhing nice"""
        msg = "Hello there!"
        if uppercase:
            msg = msg.upper()
        ctx.tell(msg)


===============================
Defining custom command parsers
===============================

--------------------------------------------------------------------------
Example with `argparse <https://docs.python.org/3/library/argparse.html>`_
--------------------------------------------------------------------------

