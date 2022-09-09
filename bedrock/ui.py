"""
This module contains icons, colors and highlighting
that may be used to decorate messages beeing sent to
the Minecraft chat.

Colors and highlighting can be activated by calling
the ``str()`` function on them or apply that styling
to a text by calling that object directly::
   
   from bedrock import ui
   
   text = f"Hello, {ui.green}World{ui.reset}!"
   text = f"Hello, {ui.green('World')}!"

Icons are just symbols that are replaced by
Minecraft automatically. So these are just
strings::
   
   from bedrock import ui
   
   text = f"Look at my friend! --> {ui.CODE_BUILDER}"

"""

class Style:
    def __init__(self, style):
        self.style = f"§{style}"
    
    def __str__(self):
        return self.style
    
    def __call__(self, text):
        return f"{self.style}{text}§r"

black = Style("0")
darkblue = Style("1")
darkgreen = Style("2")
darkaqua = Style("3")
darkred = Style("4")
darkpurple = Style("5")
gold = Style("6")
gray = grey = Style("7")
darkgray = darkgrey = Style("8")
blue = Style("9")
green = Style("a")
aqua = Style("b")
red = Style("c")
lightpurple = Style("d")
yellow = Style("e")
white = Style("f")

obfuscated = Style("k")
bold = Style("l")
italic = Style("o")
reset = Style("r")

CODE_BUILDER = "\uE103"
