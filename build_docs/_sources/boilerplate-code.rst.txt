****************
Boilerplate Code
****************

Copy-paste the code below to save some time.

.. code-block:: python3
    
    import bedrock
    
    app = bedrock.Server(
        "localhost", 6464,
        command_prefix = "$"
    )
    
    @app.command()
    async def ping(ctx):
        """Pings the server."""
        ctx.tell("Pong!")
    
    @app.command()
    async def command_name(ctx):
        """My awesome command"""
        
    
    
    app.run()
