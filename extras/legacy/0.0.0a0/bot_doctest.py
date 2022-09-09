from bedrock.ext.commands import Bot
from bedrock.docparse import BedrockDocString

bot = Bot(command_prefix = "!")

@bot.command()
async def echo(ctx, message):
    """Lets the bot output a message
    
    This conmand lets the bot display
    a message in the chat.
    
    Parameters
    ----------
    message : str
        The message to display
    
    Returns
    -------
    A message
    """
    ctx.message(message)

doc = BedrockDocString(echo.__doc__)
print(doc)

#client.run("localhost", 8888)