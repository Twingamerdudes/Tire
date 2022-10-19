import os
from CLI import *
from Tire import *
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        if not check_true_color():
            print("This terminal has to be a true color terminal (ex. powershell or cmd), there may be issuing rendering text. If you wish to contiune, press enter")
            system("pause")
        else:
            os.system("color")
        start()
    else:
        if len(sys.argv) == 2:
            if os.path.exists(sys.argv[1]) and sys.argv[1].endswith(".tire"):
                tire = Tire(open(sys.argv[1]).read())
                tire.run()
            elif os.path.exists(sys.argv[1]) and not sys.argv[1].endswith(".tire"):
                print_error("Error: File must be a .tire file.")
            else:
                print_error("Error: File does not exist. Use: python main.py <FILE_NAME>")
        else:
            print_error("Error: Invalid use. Use: python main.py <FILE_NAME>")