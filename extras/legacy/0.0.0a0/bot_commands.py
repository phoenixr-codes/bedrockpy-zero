from bedrock.ext.commands import Bot

bot = Bot(command_prefix = "!", permission = {"HortyRecord"})

@bot.event()
def on_ready(host, port):
    print(f"Ready @ {host}:{port}")

@bot.event()
async def on_connect():
    print("Connected")

@bot.command()
async def helloworld(ctx):
    print("Hello World executed")
    ctx.message("Hello World!")

bot.run("localhost", 8888)