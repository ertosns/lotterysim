from lottery import *
from threading import Thread

AVG_LEN = 5

KP_STEP=0.01
KP_SEARCH=0.0659999999999891

KI_STEP=0.01
KI_SEARCH=-0.10399999999631454

KD_STEP=0.01
KD_SEARCH=-0.030000000000002663

EPSILON=0.0001
RUNNING_TIME=1000
NODES=1000

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
    new_record=False
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
            new_record = True
            highest_acc = avg_acc
            highest_gain = (kp, ki, kd)
            with open("highest_gain.txt", 'w') as f:
                f.write(buff)
    return buff, new_record

SHIFTING = 0.05

def crawler(crawl, range_multiplier, step=0.1):
    start = None
    if crawl==KP:
        start = highest_gain[0]
    elif crawl==KI:
        start = highest_gain[1]
    elif crawl==KD:
        start = highest_gain[2]

    range_start = (start*range_multiplier if start <=0 else -1*start)
    range_end = (-1*start if start<=0 else range_multiplier*start)
    # if number of steps under 10 step resize the step to 50
    while (range_end-range_start)/step < 10:
        range_start -= SHIFTING
        range_end += SHIFTING
        step /= 10

    crawl_range = np.arange(range_start, range_end, step)
    np.random.shuffle(crawl_range)
    crawl_range = tqdm(crawl_range)
    distribution = [random.random()*NODES for i in range(NODES)]
    for i in crawl_range:
        kp = i if crawl==KP else highest_gain[0]
        ki = i if crawl==KI else highest_gain[1]
        kd = i if crawl==KD else highest_gain[2]
        buff, new_record = multi_trial_exp(kp, ki, kd, distribution, hp=high_precision)
        crawl_range.set_description('highest:{} / {}'.format(highest_acc, buff))
        if new_record:
            break

while True:
    prev_highest_gain = highest_gain
    # kp crawl
    crawler(KP, KP_RANGE_MULTIPLIER, KP_STEP)
    if highest_gain[0] == prev_highest_gain[0]:
        KP_RANGE_MULTIPLIER+=1
        KP_STEP/=10
    else:
        start = highest_gain[0]
        range_start = (start*KP_RANGE_MULTIPLIER if start <=0 else -1*start) - SHIFTING
        range_end = (-1*start if start<=0 else KP_RANGE_MULTIPLIER*start) + SHIFTING
        while (range_end - range_start)/KP_STEP >500:
            if KP_STEP < 0.1:
                KP_STEP*=10
            KP_RANGE_MULTIPLIER-=1
            #TODO (res) shouldn't the range also shrink?
            # not always true.
            # how to distinguish between thrinking range, and large step?
            # good strategy is step shoudn't > 0.1
            # range also should be > 0.8
            # what about range multiplier?

    # ki crawl
    crawler(KI, KI_RANGE_MULTIPLIER, KI_STEP)
    if highest_gain[1] == prev_highest_gain[1]:
        KI_RANGE_MULTIPLIER+=1
        KI_STEP/=10
    else:
        start = highest_gain[1]
        range_start = (start*KI_RANGE_MULTIPLIER if start <=0 else -1*start) - SHIFTING
        range_end = (-1*start if start<=0 else KI_RANGE_MULTIPLIER*start) + SHIFTING
        while (range_end - range_start)/KI_STEP >500:
            if KP_STEP < 0.1:
                KI_STEP*=10
            KI_RANGE_MULTIPLIER-=1
    # kd crawl
    crawler(KD, KD_RANGE_MULTIPLIER, KD_STEP)
    if highest_gain[2] == prev_highest_gain[2]:
        KD_RANGE_MULTIPLIER+=1
        KD_STEP/=10
    else:
        start = highest_gain[2]
        range_start = (start*KD_RANGE_MULTIPLIER if start <=0 else -1*start) - SHIFTING
        range_end = (-1*start if start<=0 else KD_RANGE_MULTIPLIER*start) + SHIFTING
        while (range_end - range_start)/KD_STEP >500:
            if KD_STEP < 0.1:
                KD_STEP*=10
            KD_RANGE_MULTIPLIER-=1
