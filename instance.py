from lottery import *
import os

os.system("rm f[0-9]*; rm leads[0-9]*; rm f.hist; rm leads.hist")

RUNNING_TIME = int(input("running time:"))


if __name__ == "__main__":
    darkies = []
    darkies += [Darkie(CONTROLLER_TYPE_DISCRETE, 0, id=id+len(darkies), kp=0.18, ki=0.02, kd=-0.1) for id in range(random.randint(5,20))]
    airdrop = 0
    for darkie in darkies:
        airdrop+=darkie.stake
    print("network airdrop: {} on {} nodes".format(airdrop, len(darkies)))
    dt = DarkfiTable(airdrop, RUNNING_TIME)
    for darkie in darkies:
        dt.add_darkie(darkie)
    dt.background(rand_running_time=False)
    dt.write()
