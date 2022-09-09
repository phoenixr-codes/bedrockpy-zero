from inspect import cleandoc

from . import ui
from .utils import get_version


bedrockpy = get_version()

WELCOME1 = f"{ui.CODE_BUILDER} {ui.bold}{ui.gold}bedrockpy{ui.reset}"

WELCOME2 = cleandoc(f"""
    | {ui.bold("version")} {".".join(map(str, bedrockpy.release))}
    | {ui.bold("release")} {"prerelease" if bedrockpy.is_prerelease else "release"}
    | {ui.red("Debug Mode")}
    |
    | connection @ {ui.yellow}%(host)s:%(port)d{ui.reset}
    |
    | Thanks for using bedrockpy {ui.red("<3")}
    | {ui.aqua("github.com/phoenixr-codes/bedrockpy")}
""")

RECEIVED = cleandoc(f"""
    {ui.bold("[bedrckpy :: debug]")}
    {ui.blue(">")} %(message)s
""")
