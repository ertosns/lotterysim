from lottery import *

TARGET=1
AIRDROP=1000
NODES=5

RUNNING_TIME = int(input("running time:"))
if __name__ == "__main__":
    dt  = DarkfiTable(AIRDROP, 0.18, 0.02, -0.1, TARGET, RUNNING_TIME)
    darkies = [Darkie(AIRDROP/float(NODES)) for i in range(NODES)]
    for darkie in darkies:
        dt.add_darkie(darkie)
    dt.background(True, False)
    dt.write()
