import sys
import temp
from Util import print_error
if sys.argv[2] == "make":
    temp.updateTemp(sys.argv[1])
else:
    if sys.argv[3] == "temp":
        try:
            temp.updateTemp(temp.getTemp().split(",")[int(sys.argv[4])])
        except IndexError:
            temp.updateTemp("Error")
            print_error("Error: index out of range")
    else:
        try:
            temp.updateTemp(sys.argv[2].split(",")[int(sys.argv[3])])
        except IndexError:
            print_error("Error: Array index out of range")
            exit(1)