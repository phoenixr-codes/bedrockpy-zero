import powerstring as ps
from powerstring.markup import XML

bedrock_block = ps.powerstring("""
    {a}{b}{b}{b}{b}{c}{d}{a}{c}{d}{c}{b}{b}{c}{b}{c}
    {b}{a}{a}{d}{a}{d}{a}{d}{b}{d}{d}{a}{e}{b}{c}{b}
    {b}{e}{b}{b}{e}{b}{b}{b}{d}{b}{c}{c}{c}{d}{c}{a}
    {c}{d}{a}{a}{c}{e}{c}{d}{c}{c}{b}{b}{b}{b}{b}{c} <blue><b>Websocket Connection</b></blue>
    {e}{b}{d}{b}{b}{b}{b}{c}{b}{b}{a}{d}{d}{a}{a}{b} <yellow>@ %(host)s:%(port)d</yellow>
    {b}{c}{c}{c}{b}{c}{c}{b}{b}{e}{c}{c}{b}{b}{e}{b}
    {d}{d}{a}{c}{a}{d}{d}{a}{c}{a}{d}{d}{a}{d}{b}{e}
    {c}{c}{c}{b}{c}{c}{c}{b}{b}{e}{b}{b}{c}{b}{a}{c}
    {a}{d}{d}{c}{b}{b}{c}{c}{a}{d}{d}{a}{d}{d}{d}{d}
    {c}{b}{b}{e}{b}{c}{b}{c}{b}{a}{c}{b}{b}{b}{d}{a}
    {a}{a}{d}{b}{a}{d}{d}{b}{e}{b}{d}{d}{d}{a}{b}{b}
    {e}{c}{c}{c}{b}{b}{c}{a}{d}{d}{c}{a}{a}{d}{d}{e} * Disable <cyan>Require Encrypted Websockets</cyan>
    {c}{b}{b}{b}{a}{c}{b}{b}{a}{d}{b}{b}{b}{b}{b}{c}   in the settings
    {a}{d}{a}{d}{c}{e}{c}{b}{b}{b}{e}{b}{c}{a}{d}{d} * Type <cyan>/connect %(host)s:%(port)s</cyan>
    {a}{a}{c}{b}{b}{c}{b}{b}{c}{a}{d}{d}{c}{b}{b}{c}   in the chat
    {b}{e}{b}{b}{e}{d}{d}{a}{b}{c}{a}{e}{b}{b}{c}{a}
""", plugin = XML(**ps.ansi.__dict__))

banner = bedrock_block.format(
    a = ps.color("  ", ps.Color.from_rgb(99, 99, 99).bg),
    b = ps.color("  ", ps.Color.from_rgb(51, 51, 51).bg),
    c = ps.color("  ", ps.Color.from_rgb(87, 87, 87).bg),
    d = ps.color("  ", ps.Color.from_rgb(151, 151, 151).bg),
    e = ps.color("  ", ps.Color.from_rgb(34, 34, 34).bg)
)

print(banner % {"host": "127.0.0.1", "port": 6464})