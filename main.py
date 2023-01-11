from lottery import *

AVG_LEN = 10

KP_STEP=0.03
KP_SEARCH_START=-0.3
KP_SEARCH_END=0.3

KI_STEP=0.03
KI_SEARCH_START=-0.1
KI_SEARCH_END=0.1

KD_STEP=0.03
KD_SEARCH_START=-0.1
KD_SEARCH_END=0.1

EPSILON=0.0001
RUNNING_TIME=1000

AIRDROP=1000
NODES=5

randomize_nodes_str = input("randomize number of nodes (y/n):")
randomize_nodes = True if randomize_nodes_str.lower()=="y" else False

discrete_pid_str = input("discrete controller (y/n):")
discrete_pid = True if discrete_pid_str.lower()=="y" else False

rand_running_time_str = input("random running time (y/n):")
rand_running_time = True if rand_running_time_str.lower()=="y" else False

debug_str = input("debug mode (y/n):")
debug = True if debug_str.lower()=="y" else False


if __name__ == "__main__":
    # kp
    accuracy = []
    for kp in tqdm(np.arange(KP_SEARCH_START, KP_SEARCH_END, KP_STEP)):
        # ki
        for ki in np.arange(KI_SEARCH_START, KI_SEARCH_END, KI_STEP):
            # kd
            for kd in np.arange(KD_SEARCH_START, KD_SEARCH_END, KD_STEP):
                target = 1
                accs = []
                for i in range(0, AVG_LEN):
                    dt = DarkfiTable(AIRDROP, kp, ki, kd, target, RUNNING_TIME)
                    darkie_accs = []
                    sum_airdrops = 0
                    # random nodes
                    RND_NODES = random.randint(1, NODES) if randomize_nodes else NODES
                    for idx in range(0,RND_NODES):
                        # random airdrops
                        darkie_airdrop = None
                        if idx == RND_NODES-1:
                            darkie_airdrop = AIRDROP - sum_airdrops
                        else:
                            remaining_stake = (AIRDROP-RND_NODES)-sum_airdrops
                            if remaining_stake <= 1:
                                continue
                            darkie_airdrop = random.randrange(1, remaining_stake)
                        sum_airdrops += darkie_airdrop
                        darkie = Darkie(darkie_airdrop)
                        dt.add_darkie(darkie)
                        darkie_acc = dt.background(discrete_pid, rand_running_time, debug)
                        darkie_accs+=[darkie_acc]
                    acc = sum(darkie_accs)/(float(len(darkie_accs))+EPSILON)
                    accs+=[acc]
                avg_acc = sum(accs)/float(AVG_LEN)
                gains = (avg_acc, (kp, ki, kd))
                accuracy+=[gains]
    accuracy=sorted(accuracy, key=lambda i: i[0], reverse=True)
    with open("gains.txt", "w") as f:
        buff=''
        for gain in accuracy:
            line=str(gain[0])+','+','.join([str(i) for i in gain[1]])+'\n'
            buff+=line
            f.write(buff)
