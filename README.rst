*********
bedrockpy
*********

bedrockpy is a library that handles a websocket
connection between your Minecraft world and your
server. This library allows you to create custom
commands and react to several events.


=========
Important
=========

This library is not meant for creating add-ons,
plugins or similar things. If you are however
looking for creating such creations, you might
take a look at `Microsofts official Minecraft
Bedrock documentation
<https://docs.microsoft.com/en-us/minecraft/creator/>`_

This library is meant to combine python knowledge
with Minecraft or execute Python code on systems
that do not provide full add-on support (such as
Bedrock Edition on Consoles).


====================
A very small example
====================

This demonstrates the basic structure of a bot
Don't worry, there is way more to create!

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


`Documentation <https://phoenixr-codes.github.io/bedrockpy/>`_


NOT AN OFFICIAL MINECRAFT PRODUCT.
NOT APPROVED BY OR ASSOCIATED WITH MOJANG.
