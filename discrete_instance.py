from lottery import *

RUNNING_TIME=500
TARGET=1
AIRDROP=10
NODES=5

if __name__ == "__main__":
    dt  = DarkfiTable(AIRDROP, -0.8, 0.6, 0.8, TARGET, RUNNING_TIME)
    darkies = [Darkie(AIRDROP/float(NODES)) for i in range(NODES)]
    for darkie in darkies:
        dt.add_darkie(darkie)
    dt.background()
    dt.write()
