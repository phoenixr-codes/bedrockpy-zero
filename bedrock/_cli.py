from argparse import ArgumentParser
from . import Server

def main():
    parser = ArgumentParser()
    
    parser.add_argument("host",
        default = "127.0.0.1"
    )
    
    parser.add_argument("port",
        default = 6464,
        type = int
    )
    
    parser.add_argument("-p", "--prefix",
        default = "!"
    )
    
    args = parser.parse_args()
    
    app = Server(
        args.host, args.port,
        command_prefix = args.prefix
    )
    
    try:
        app.run()
    except KeyboardInterrupt:
        app.close()

if __name__ == "__main__":
    main()
