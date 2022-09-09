"""
Example showing how to use commands by using
a qr code generator.
"""

import bedrock
from PIL import Image
import qrcode

app = bedrock.Server(
    "localhost", 8080,
    command_prefix = "qr ",
    debug = True
)

@app.command()
async def place(
    ctx,
    data,
    size: int = 64
):
    im = qrcode.make(data).resize((size, size))
    
    x = z = 1
    for color in im.getdata():
        await ctx.execute(f"setblock ~{x} ~-1 ~{z} concrete {0 if color == 0 else 15}")
        
        if x % size == 0:
            x = 1
            z += 1
        
        else:
            x += 1

app.run()
