from lottery import *
from threading import Thread

AVG_LEN = 5

KP_STEP=0.01
KP_SEARCH=-1.8457457784393227e-15

KI_STEP=0.01
KI_SEARCH=-0.11934999999953416

KD_STEP=0.01
KD_SEARCH=-1.3322676295501878e-15

EPSILON=0.0001
RUNNING_TIME=100
NODES=500

highest_acc = 0

KP='kp'
KI='ki'
KD='kd'

KP_RANGE_MULTIPLIER = 2
KI_RANGE_MULTIPLIER = 2
KD_RANGE_MULTIPLIER = 2

highest_gain = (KP_SEARCH, KI_SEARCH, KD_SEARCH)


high_precision_str = input("high precision arith (slooow) (y/n):")
high_precision = True if high_precision_str.lower()=="y" else False

randomize_nodes_str = input("randomize number of nodes (y/n):")
randomize_nodes = True if randomize_nodes_str.lower()=="y" else False

rand_running_time_str = input("random running time (y/n):")
rand_running_time = True if rand_running_time_str.lower()=="y" else False

debug_str = input("debug mode (y/n):")
debug = True if debug_str.lower()=="y" else False

def experiment(accs=[], controller_type=CONTROLLER_TYPE_DISCRETE, kp=0, ki=0, kd=0, distribution=[], hp=False):
    dt = DarkfiTable(sum(distribution), RUNNING_TIME, controller_type, kp=kp, ki=ki, kd=kd)
    RND_NODES = random.randint(5, NODES) if randomize_nodes else NODES
    for idx in range(0,RND_NODES):
        darkie = Darkie(distribution[idx])
        dt.add_darkie(darkie)
    acc = dt.background(rand_running_time, hp)
    accs+=[acc]
    return acc


def multi_trial_exp(kp, ki, kd, distribution = [], hp=False):
    global highest_acc
    global highest_gain
    exp_threads = []
    accs = []
    for i in range(0, AVG_LEN):
        acc = experiment(accs, CONTROLLER_TYPE_DISCRETE, kp=kp, ki=ki, kd=kd, distribution=distribution, hp=hp)
        accs += [acc]
    avg_acc = sum(accs)/float(AVG_LEN)
    buff = 'accuracy:{}, kp: {}, ki:{}, kd:{}'.format(avg_acc, kp, ki, kd)
    if avg_acc > 0:
        gain = (kp, ki, kd)
        acc_gain = (avg_acc, gain)
        if avg_acc > highest_acc:
            highest_acc = avg_acc
            highest_gain = (kp, ki, kd)
            with open("highest_gain.txt", 'w') as f:
                f.write(buff)
    return buff

SHIFTING = 0.05

def crawler(crawl, range_multiplier, step=0.1):
    start = None
    if crawl==KP:
        start = highest_gain[0]
    elif crawl==KI:
        start = highest_gain[1]
    elif crawl==KD:
        start = highest_gain[2]

    range_start = (start*range_multiplier if start <=0 else -1*start) - SHIFTING
    range_end = (-1*start if start<=0 else range_multiplier*start) + SHIFTING
    # if number of steps under 10 step resize the step to 50
    if (range_end-range_start)/step < 10:
        step = (range_end-range_start)/50

    crawl_range = tqdm(np.arange(range_start, range_end, step))
    distribution = [random.random() for i in range(NODES)]
    for i in crawl_range:
        kp = i if crawl==KP else highest_gain[0]
        ki = i if crawl==KI else highest_gain[1]
        kd = i if crawl==KD else highest_gain[2]
        buff = multi_trial_exp(kp, ki, kd, distribution, hp=high_precision)
        crawl_range.set_description('highest:{} / {}'.format(highest_acc, buff))

while True:
    prev_highest_gain = highest_gain
    # kp crawl
    crawler(KP, KP_RANGE_MULTIPLIER, KP_STEP)
    if highest_gain[0] == prev_highest_gain[0]:
        KP_RANGE_MULTIPLIER+=1
        KP_STEP/=10
    # ki crawl
    crawler(KI, KI_RANGE_MULTIPLIER, KI_STEP)
    if highest_gain[1] == prev_highest_gain[1]:
        KI_RANGE_MULTIPLIER+=1
        KI_STEP/=10
    # kd crawl
    crawler(KD, KD_RANGE_MULTIPLIER, KD_STEP)
    if highest_gain[2] == prev_highest_gain[2]:
        KD_RANGE_MULTIPLIER+=1
        KD_STEP/=10
