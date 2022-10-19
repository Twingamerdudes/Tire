import sys
import temp
if sys.argv[3] == "temp":
    temp.updateTemp(temp.getTemp().split(sys.argv[2]))
else:
    temp.updateTemp(sys.argv[1].split(sys.argv[2]))