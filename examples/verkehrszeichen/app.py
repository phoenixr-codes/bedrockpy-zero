from math import sqrt
from pathlib import Path

import bedrock
from bedrock.utils import boolean
from PIL import Image


PALETTE = {
    (255, 255, 255): "concrete  0", # white
    (  0,   0,   0): "concrete 15", # black
    (255,   0,   0): "concrete 14", # red
    (  0, 255,   0): "concrete  5", # green
    (  0,   0, 255): "concrete  3", # blue
    (255, 255,   0): "concrete  4", # yellow
    (127, 127, 127): "concrete  8", # gray
}


def square_image(im: Image):
    size = max(im.size)
    bg = Image.new("RGB", (size, size), "white")
    bg.paste(im, (
        int(
            (size - im.size[0]) / 2
        ),
        int(
            (size - im.size[1]) / 2
        )
    ))
    return bg


server = bedrock.Server(
    "localhost", 6464,
    command_prefix = "#",
    debug = True
)


@server.command()
async def place(ctx, filename, flipped: boolean = False, size: int = 128):
    Y = "-1"
    file = Path("verkehrszeichen") / (filename + ".jpg")
    
    if not file.exists():
        await ctx.tell("file does not exist")
        return
    
    im = Image.open(file).convert("RGB")
    
    # flip if necessary
    if flipped:
        im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    
    # make image to square
    if im.size[0] != im.size[1]:
        im = square_image(im)
    
    # generate pixelized image
    im = im.resize((size, size), resample = Image.Resampling.BILINEAR)
    
    # add tickingareas
    for i in range(1, 11):
        x = 128
        z = i * 16
        area = f"~ ~{Y} ~{z - 16}  ~{x} ~{Y} ~{z}"
        
        # we can ignore any issues regarding already
        # existing tickingareas
        await ctx.run(f"tickingarea add {area} tmp{i}")
    
    
    # place blocks
    x = z = 1
    for r, g, b in im.getdata():
        diffs = {}
        for mc_rgb, block in PALETTE.items():
            diff = sqrt(
                abs(r - mc_rgb[0]) ** 2 +
                abs(g - mc_rgb[1]) ** 2 +
                abs(b - mc_rgb[2]) ** 2
            )
            diffs[diff] = block
        
        block = diffs[min(diffs.keys())]
        await ctx.run(f"setblock ~{x - 1} ~{Y} ~{z - 1} {block}")
        
        
        if x % size == 0:
            x = 1
            z += 1
        
        else:
            x += 1
    
    # remove tickingareas
    for i in range(1, 11):
        await ctx.run(f"tickingarea remove tmp{i}")
    
    await ctx.tell(f"Done placing {filename}!")


@server.command()
async def ping(ctx):
    await ctx.reply("Pong!")


server.run()
