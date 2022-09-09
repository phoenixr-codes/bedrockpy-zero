import argparse
from pathlib import Path
import shlex

import bedrock
from bedrock.command_parsers import CommandParser
from bedrock.commands import CommandError


PROG = Path(__file__).stem

# Be aware that some actions force printing
# to the console and quit such as 'version'.
# You should not use them and instead use a
# workaround.


class MyCommandParser(CommandParser):
    def __init__(self):
        self.prog = __name__
        self.p = argparse.ArgumentParser(prog = PROG)
    
    async def parse(self, ctx, string: str) -> None:
        try:
            # Because argparse is meant for
            # console applications, it tends
            # to exit the programm. We can
            # however prevent it with a try-
            # except block.
            
            args = self.p.parse_args(shlex.split(string))
            
            if args.version:
                output = "1.0.0"
            
            await ctx.tell(output)
        
        except SystemExit:
            await ctx.reply_error(
                "an error occured; check error output for "
                "more information"
            )

parser = MyCommandParser()
parser.p.add_argument("-v", "--version")

app = bedrock.Server(
    "localhost", 6464,
    command_prefix = PROG + " ",
    command_parser = parser
)

app.run()
