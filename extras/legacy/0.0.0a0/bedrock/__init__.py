#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A Bot for Minecraft: Bedrock Edition programmed in python using websockets


Summary
=======

Minecraft Bedrock Edition allows you to
connect to a websocket connection via the
`wsserver` or the `connect` command.
Minecraft will send events and responses
to the websocket and will execute commands
sent from the websocket.


Connection On Unsupported Platforms
===================================

Some platforms do not allow to connect to
a websocket but it's still possible to leta
the bot execute commands and listen to events.
By simply joining the unsupported on a suported
device with operator rights in the world you
can create a connection to a websocket.


Disclaimer
==========

You may have to disable "Require Encrypted
Websockets" in the settings in Minecraft in
order to make it work.
You may take a look at the Scripting API which
allows you create mods.
(https://www.minecraft.net/en-us/article/scripting-api-now-public-beta)

bedrock.py is not affiliated, associated,
authorized, endorsed by, or in any way
officially connected with Mojang AB or
Microsoft.
The name Minecraft as well as any related names,
marks, emblems and images are registered
trademarks of their respective owners.
"""

__author__ = "phoenixR"
__version__ = "0.0.2b1"
__copyright__ = "Copyright (c) 2021-2022 phoenixR"
__license__ = "MIT"


from .client import *