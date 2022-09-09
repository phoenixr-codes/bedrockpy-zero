bedrock.py ![](https://raw.githubusercontent.com/The-phoenixR/bedrockpy/main/bedrockpy-logo-64.png "bedrockpy")
===============================================================================================================

A Bot for Minecraft: Bedrock Edition programmed in python using websockets

[![Downloads](https://static.pepy.tech/personalized-badge/bedrockpy?period=total&units=international_system&left_color=black&right_color=blue&left_text=Downloads)](https://pepy.tech/project/bedrockpy)

Minecraft Bedrock Edition allows you to
connect to a websocket connection via the
`wsserver` or the `connect` command.
Minecraft will send events and responses
to the websocket and will execute commands
sent from the websocket.


Connection On Unsupported Platforms
-----------------------------------

Some platforms do not allow to connect to
a websocket but it's still possible to leta
the bot execute commands and listen to events.
By simply joining the unsupported on a suported
device with operator rights in the world you
can create a connection to a websocket.


---


Contents
--------

1. Installation
2. Quickstart


Installation
------------

```
pip install bedrockpy
```


Quickstart
----------

```python
import bedrock

client = bedrock.Client()

@client.event()
def on_ready(host, port):
    print(f"Ready. Type /connect {host}:{port} in Minecraft")

@client.event()
async def on_connect():
    print("Connected!")

client.run("localhost", 1234)
```


Not wotking? Make sure you ...
------------------------------

- disabled `Require Encrypted Websockets` in the settings
- have the rights to use the `connect`/`wsserver` command (operator status)
- are not already connected to another connection
- have used the correct command syntax
- have not used the port for something else already
- are using Minecraft Bedrock Edition version 1.0.0 or higher


Disclaimer
----------

You may take a look at the Scripting API which
allows you create mods.
(https://www.minecraft.net/en-us/article/scripting-api-now-public-beta)

bedrockpy is not affiliated, associated,
authorized, endorsed by, or in any way
officially connected with Mojang AB or
Microsoft.
The name Minecraft as well as any related names,
marks, emblems and images are registered
trademarks of their respective owners.

