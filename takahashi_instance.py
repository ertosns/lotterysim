from lottery import *

TARGET=1
AIRDROP=1000
NODES=5

RUNNING_TIME = int(input("running time:"))
if __name__ == "__main__":
    dt  = DarkfiTable(AIRDROP, 0, 0, 0, TARGET, RUNNING_TIME, -2, -0.6, 0.25, -0.3)
    darkies = [Darkie(AIRDROP/float(NODES)) for i in range(NODES)]
    for darkie in darkies:
        dt.add_darkie(darkie)
    dt.background(True, False)
    dt.write()
