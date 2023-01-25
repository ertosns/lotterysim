from lottery import *

AVG_LEN = 5

KC_STEP=0.1
KC_SEARCH_START=-2.3
KC_SEARCH_END=-1.9

TI_STEP=0.05
TI_SEARCH_START=-0.7
TI_SEARCH_END=-0.5

TD_STEP=0.05
TD_SEARCH_START=0.1
TD_SEARCH_END=0.3

TS_STEP=0.05
TS_SEARCH_START=-0.4
TS_SEARCH_END=-0.2

EPSILON=0.0001
RUNNING_TIME=1000

NODES=30

randomize_nodes_str = input("randomize number of nodes (y/n):")
randomize_nodes = True if randomize_nodes_str.lower()=="y" else False

rand_running_time_str = input("random running time (y/n):")
rand_running_time = True if rand_running_time_str.lower()=="y" else False

debug_str = input("debug mode (y/n):")
debug = True if debug_str.lower()=="y" else False

target = 1
accuracy = []
# Kc
for kc in tqdm(np.arange(KC_SEARCH_START, KC_SEARCH_END, KC_STEP)):
    if kc == 0:
        continue
    # Ti
    for ti in np.arange(TI_SEARCH_START, TI_SEARCH_END, TI_STEP):
        if ti == 0:
            continue
        # Td
        for td in np.arange(TD_SEARCH_START, TD_SEARCH_END, TD_STEP):
            if td == 0:
                continue
            # Ts
            for ts in np.arange(TS_SEARCH_START, TS_SEARCH_END, TS_STEP):
                if ts == 0:
                    continue
                accs = []
                for i in range(0, AVG_LEN):
                    dt = DarkfiTable(0, RUNNING_TIME)
                    darkie_accs = []
                    #sum_airdrops = 0
                    # random nodes
                    RND_NODES = random.randint(5, NODES) if randomize_nodes else NODES
                    for idx in range(0,RND_NODES):
                        # random airdrops
                        #darkie_airdrop = None
                        #if idx == RND_NODES-1:
                            #darkie_airdrop = AIRDROP - sum_airdrops
                        #else:
                            #remaining_stake = (AIRDROP-RND_NODES)-sum_airdrops
                            #if remaining_stake <= 1:
                                #continue
                            #darkie_airdrop = random.randrange(1, remaining_stake)
                        #sum_airdrops += darkie_airdrop
                        darkie = Darkie(CONTROLLER_TYPE_TAKAHASHI, 0, ti=ti, td=td, ts=ts, kc=kc)
                        dt.add_darkie(darkie)
                        darkie_acc = dt.background(rand_running_time, debug)
                        darkie_accs+=[darkie_acc]
                    acc = sum(darkie_accs)/(float(len(darkie_accs))+EPSILON)
                    accs+=[acc]
                avg_acc = sum(accs)/float(AVG_LEN)
                gains = (avg_acc, (kc, ti, td, ts))
                accuracy+=[gains]


accuracy=sorted(accuracy, key=lambda i: i[0], reverse=True)
with open("takahashi_gains.txt", "w") as f:
    buff=''
    for gain in accuracy:
        line=str(gain[0])+','+','.join([str(i) for i in gain[1]])+'\n'
        buff+=line
        f.write(buff)
