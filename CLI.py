from Util import *
from Tire import *

def start():
    print_color("""___________ __                 _________  ____     ___ 
\__    ___/|__|______   ____   \_   ___ \|    |   |   |
  |    |   |  \_  __ \_/ __ \  /    \  \/|    |   |   |
  |    |   |  ||  | \/\  ___/  \     \___|    |___|   |
  |____|   |__||__|    \___  >  \______  /_______ \___|
                           \/          \/        \/ """, 51, 184, 100)
    print_color("Check out our GitHub page: (Work in progress)", 24, 154, 211)
    while True:
        command = input("> ")
        if command.split(" ")[0] == "run":
            if not command.split(" ")[1].endswith(".tire"):
                print_error("Error: File must be a .tire file.")
            tire = Tire(open(command.split()[1]).read())
            tire.run()
        else:
            tire = Tire(command)
            tire.run()