**********
Quickstart
**********

============
Installation
============

Install with pip

.. code-block:: bash
    
    pip install bedrockpy
    
    # or include uvloop:
    pip install bedrockpy[uvloop]

and import it in python with

.. code-block:: python3
    
    import bedrock

======
Set-Up
======

#. In order to use this library with Minecraft,
   you need to configure one setting in the game:
   Disable ``Require Encrypted Websockets`` at
   ``User Profile and Settings``.

#. Run ``bedrockws serve`` in your terminal to
   test if everything works.
   
   .. note::
      You might have to specify a port by using
      ``bedrockws serve 1234``.

#. Join any Minecraft World where you have an
   operator status. Use one of the commands
   ``/connect`` or ``/wsserver`` to establish a
   connection.
   
   .. code-block::
       
       /connect localhost:6464
       

#. Now you should see a message popping up
   in the Minecraft chat sent by the server.


========================
Creating a custom server
========================

You can create a customized server with commands
by creating a python program.

First, import ``bedrockpy``:

.. code-block:: python3
    
    import bedrock

Now initialise the server:

.. code-block:: python3
    
    app = bedrock.Server(
        "localhost", 6464,
        command_prefix = "$"
    )

Add a notification that the server is ready:

.. code-block:: python3
    
    @app.event
    async def on_ready(ctx):
        print("Ready!")

Then create a command:

.. code-block:: python3
    
    @app.command()
    async def hello(ctx):
        """say hello"""
        ctx.tell("Hello, World!")

And finally, start the server:

.. code-block:: python3
    
    app.run()

All combined and it should look like this:

.. code-block:: python3
   
   import bedrock
   
   app = bedrock.Server(
       "localhost", 6464,
       command_prefix = "$"
   )
   
   @app.event
   async def on_ready(ctx):
       print("Ready!")
   
   @app.command()
   async def hello(ctx):
       """say hello"""
       ctx.tell("Hello, World!")
   
   app.run()
