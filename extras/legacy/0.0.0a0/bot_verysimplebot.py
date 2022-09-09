from bedrock import Client

client = Client()

@client.event()
def on_ready(host, port):
    print(f"Ready @ {host}:{port}")

@client.event()
async def on_connect():
    print("Connected")

client.run("localhost", 8888)