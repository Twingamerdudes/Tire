def updateTemp(value):
    open("temp", "w").write(value)
def getTemp():
    return open("temp", "r").read()