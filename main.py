from lottery import *
from threading import Thread

AVG_LEN = 1

KP_STEP=0.1
KP_SEARCH_START=-0.1
KP_SEARCH_END=0.2

KI_STEP=0.1
KI_SEARCH_START=-0.1
KI_SEARCH_END=0.1

KD_STEP=0.1
KD_SEARCH_START=-0.1
KD_SEARCH_END=0.1

EPSILON=0.0001
RUNNING_TIME=1000

#AIRDROP=1000
NODES=30

randomize_nodes_str = input("randomize number of nodes (y/n):")
randomize_nodes = True if randomize_nodes_str.lower()=="y" else False

rand_running_time_str = input("random running time (y/n):")
rand_running_time = True if rand_running_time_str.lower()=="y" else False

debug_str = input("debug mode (y/n):")
debug = True if debug_str.lower()=="y" else False

def experiment(accs=[], controller_type=CONTROLLER_TYPE_DISCRETE, kp=0, ki=0, kd=0, airdrop=0):
    dt = DarkfiTable(0, RUNNING_TIME, controller_type, kp=kp, ki=ki, kd=kd)
    RND_NODES = random.randint(5, NODES) if randomize_nodes else NODES
    for idx in range(0,RND_NODES):
        darkie = Darkie(airdrop)
        dt.add_darkie(darkie)
    acc = dt.background(rand_running_time)
    accs+=[acc]
    return acc

def multi_trial_exp(gains, kp, ki, kd):
    experiment_accs = []
    exp_threads = []
    for i in range(0, AVG_LEN):
        exp_thread = Thread(target=experiment, args=[experiment_accs, CONTROLLER_TYPE_DISCRETE, kp, ki, kd])
        exp_thread.start()
    for thread in exp_threads:
        thread.join()
    avg_acc = sum(experiment_accs)/float(AVG_LEN)
    gain = (avg_acc, (kp, ki, kd))
    gains += [gain]


def single_trial_exp(gains, kp, ki, kd):
    acc = experiment(kp=kp, ki=ki, kd=kd)
    if acc > 0:
        gain = (acc, (kp, ki, kd))
        gains += [gain]


gains = []
if __name__ == "__main__":
    # kp
    gains_threads = []
    for kp in tqdm(np.arange(KP_SEARCH_START, KP_SEARCH_END, KP_STEP)):
        # ki
        for ki in np.arange(KI_SEARCH_START, KI_SEARCH_END, KI_STEP):
            # kd
            for kd in np.arange(KD_SEARCH_START, KD_SEARCH_END, KD_STEP):
                thread = Thread(target=single_trial_exp, args=[gains, kp, ki, kd])
                thread.start()
                gains_threads += [thread]
    for th in tqdm(gains_threads):
        th.join()
    gains=sorted(gains, key=lambda i: i[0], reverse=True)
    with open("gains.txt", "w") as f:
        buff=''
        for gain in gains:
            line=str(gain[0])+',' +','.join([str(i) for i in gain[1]])+'\n'
            buff+=line
            f.write(buff)
