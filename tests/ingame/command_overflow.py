"""
Because Minecraft only accepts 100 command
requests at a time before responding to them,
the server needs to handle that potential
comflict.
"""

import bedrock

app = bedrock.Server(
    "localhost", 80,
    command_prefix = '.',
    debug = True
)

@app.command()
def overflow(ctx, amount: int = 110):
    for i in range(amount):
        ctx.execute('tellraw @a {"rawtext":[{"text":"Message #%d"}]}' % i)

app.run()