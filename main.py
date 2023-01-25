from lottery import *
from threading import Thread

AVG_LEN = 3

KP_STEP=0.1
KP_SEARCH_START=-0.3
KP_SEARCH_END=0.3

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

    
def single_runtime(dt, darkie_accs, controller=CONTROLLER_TYPE_DISCRETE, kp=0, ki=0, kd=0):
    darkie = Darkie(controller, 0, kp=kp, ki=ki, kd=kd)
    dt.add_darkie(darkie)
    darkie_acc = dt.background(rand_running_time)
    darkie_accs+=[darkie_acc]

def experiment(threads, accs, controller=CONTROLLER_TYPE_DISCRETE, kp=0, ki=0, kd=0):
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
        thread = Thread(target=single_runtime, args=(dt, darkie_accs, controller, kp, ki, kd))
        thread.start()
        threads += [thread]
    for thread in threads:
        thread.join()
    acc = sum(darkie_accs)/(float(len(darkie_accs))+EPSILON)
    accs+=[acc]


#dt = DarkfiTable(0, RUNNING_TIME)
#darkie_accs = []

accuracy = []
if __name__ == "__main__":
    # kp
    
    for kp in tqdm(np.arange(KP_SEARCH_START, KP_SEARCH_END, KP_STEP)):
        # ki
        for ki in np.arange(KI_SEARCH_START, KI_SEARCH_END, KI_STEP):
            # kd
            for kd in np.arange(KD_SEARCH_START, KD_SEARCH_END, KD_STEP):
                target = 1
                experiment_accs = []
                exp_threads = []
                for i in range(0, AVG_LEN):
                    exp_thread = Thread(target=experiment, args=(exp_threads, experiment_accs, CONTROLLER_TYPE_DISCRETE, kp, ki, kd))
                    exp_thread.start()
                for thread in exp_threads:
                    thread.join()
                avg_acc = sum(experiment_accs)/float(AVG_LEN)
                gains = (avg_acc, (kp, ki, kd))
                accuracy+=[gains]
    accuracy=sorted(accuracy, key=lambda i: i[0], reverse=True)
    with open("gains.txt", "w") as f:
        buff=''
        for gain in accuracy:
            line=str(gain[0])+',' +','.join([str(i) for i in gain[1]])+'\n'
            buff+=line
            f.write(buff)
