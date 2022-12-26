from lottery import *

AVG_LEN = 10

KP_STEP=0.05
KP_SEARCH_START=0.4
KP_SEARCH_END=0.9

KI_STEP=0.05
KI_SEARCH_START=0.4
KI_SEARCH_END=0.9

KD_STEP=0.1
KD_SEARCH_START=-1
KD_SEARCH_END=1
EPSILON=0.0001


if __name__ == "__main__":
    # kp
    accuracy = []
    for kp in tqdm(np.arange(KP_SEARCH_START, KP_SEARCH_END, KP_STEP)):
        percent = (kp+3)*100/6
        # ki
        for ki in np.arange(KI_SEARCH_START, KI_SEARCH_END, KI_STEP):
            # kd
            for kd in np.arange(KD_SEARCH_START, KD_SEARCH_END, KD_STEP):
                target = 1
                accs = []
                for i in range(0, AVG_LEN):
                    dt = DarkfiTable(AIRDROP, kp, ki, kd, target)
                    darkie_accs = []
                    sum_airdrops = 0
                    # random nodes
                    RND_NODES=random.randint(1,NODES)
                    for idx in range(3,RND_NODES):
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
                        darkie_acc = dt.background()
                        darkie_accs+=[darkie_acc]
                    acc = sum(darkie_accs)/(float(len(darkie_accs))+EPSILON)
                    accs+=[acc]
                avg_acc = sum(accs)/float(AVG_LEN)
                gains = (avg_acc, (kp, ki, kd))
                accuracy.append(gains)
                with open("gains_buf.txt", "a+") as f:
                    line=str(gains[0])+','+','.join([str(i) for i in gains[1]])+'\n'
                    f.write(line)
    accuracy=sorted(accuracy, key=lambda i: i[0], reverse=True)
    with open("gains.txt", "w+") as f:
        buff=''
        for gain in accuracy:
            line=str(gain[0])+','+','.join([str(i) for i in gains[1]])+'\n'
            buff+=line
        f.write(buff)
