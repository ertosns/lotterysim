from lottery import *
import os

os.system("rm f[0-9]*")

RUNNING_TIME = int(input("running time:"))


if __name__ == "__main__":
    darkies = []
    #darkies += [Darkie(CONTROLLER_TYPE_DISCRETE, random.randint(0,1000), id=i, kp=0.18, ki=0.02, kd=-0.1) for i in range(2)]
    darkies += [Darkie(CONTROLLER_TYPE_DISCRETE, 0, id=id+len(darkies), kp=0.18, ki=0.02, kd=-0.1) for id in range(random.randint(1,100))]
    airdrop = 0
    for darkie in darkies:
        airdrop+=darkie.stake
    dt = DarkfiTable(airdrop, RUNNING_TIME)
    for darkie in darkies:
        dt.add_darkie(darkie)
    dt.background(rand_running_time=True)
    dt.write()
