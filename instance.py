from lottery import *
import os
import numpy
os.system("rm f.hist; rm leads.hist")

RUNNING_TIME = int(input("running time:"))
ERC20DRK=2.1*10**9
NODES=1000

if __name__ == "__main__":
    darkies = []
    egalitarian = ERC20DRK/NODES
    darkies += [ Darkie(random.gauss(egalitarian, egalitarian*0.1)) for id in range(int(NODES/4)) ]
    #darkies += [Darkie(1) for _ in range(NODES*2)]
    airdrop = ERC20DRK
    effective_airdrop  = 0
    for darkie in darkies:
        effective_airdrop+=darkie.stake
    print("network airdrop: {}, staked token: {}/{}% on {} nodes".format(airdrop, effective_airdrop, effective_airdrop/airdrop*100, len(darkies)))
    dt = DarkfiTable(airdrop, RUNNING_TIME, CONTROLLER_TYPE_DISCRETE, kp=0.005999999999989028, ki=-0.005999999985257798, kd=0.01299999999999478)
    for darkie in darkies:
        dt.add_darkie(darkie)
    acc = dt.background(rand_running_time=False)
    print('acc: {}'.format(acc))
    dt.write()
