import random
import math
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

L = 28948022309329048855892746252171976963363056481941560715954676764349967630337
N_TERM = 2
AIRDROP = 10
REWARD = 3
NODES = 5
RUNNING_TIME = 50
# naive factorial
def fact(n):
    assert (n>0)
    n = int(n)
    if n==1:
        return 1
    elif n==2:
        return 2
    else:
        return n * fact(n-1)


class State:
    def __init__(self, f, T, won):
        self.f=f
        self.T=T
        self.won=won

# all inputs to this function are integers
# sigmas are public
# stake is private
def approx_target_in_zk(sigmas, stake):
    # both sigma_1, sigma_2 are constants, if f is a constant.
    # if f is constant then sigma_12, sigma_2
    # this dictates that tuning need to be hardcoded,
    # secondly the reward, or at least the total stake in the network,
    # can't be anonymous, should be public.
    T = [sigma*stake**(i+1) for i, sigma in enumerate(sigmas)]
    return -1*sum(T)

def rnd():
    return random.random()


def lottery(T):
    y =  rnd() * L
    #print("y: ", y)
    #print("T: ", T)
    return y < T

class Tunning:
    def __init__(self, f, Sigma):
        self.f=f
        self.sigma=Sigma

class Darkie:
    def __init__(self, airdrop):
        self.stake = airdrop
        self.state = None
        self.tunning = None

    def run(self):
        f = self.tunning.f
        #print("f: ", f)
        Sigma = self.tunning.sigma
        k=N_TERM
        x = (1-f)
        c = math.log(x)
        sigmas = [int((c/Sigma)**i * (L/fact(i))) for i in range(1, k+1)]
        T = approx_target_in_zk(sigmas, self.stake)
        is_lead = lottery(T)
        self.state = State(f, T, is_lead)

    def set_in(self, tunning):
        self.tunning =tunning

    def update_state(self):
        self.stake+=REWARD

PREV_FEEDBACK=0
class PID:
    def __init__(self, kp, ki, kd, T, target):
        self.Kp = kp
        self.Ki = ki
        self.Kd = kd
        self.T = T
        self.target = target
        self.prev_feedback = PREV_FEEDBACK
        self.feedback_hist = [PREV_FEEDBACK]

    def pid(self, feedback):
        ret =  (self.Kp * self.proportional(feedback))
        + (self.Ki * self.integral(feedback))
        + (self.Kd * self.derivative(feedback))
        self.feedback_hist+=[feedback]
        self.prev_feedback=feedback
        return ret

    def pid_clipped(self, feedback):
        pid_value = self.pid(feedback)
        if pid_value == 0.0:
            return 0.01
        elif pid_value >= 1:
            return  0.99
        return pid_value

    def error(self, feedback):
        return self.target - feedback

    def proportional(self,  feedback):
        return self.error(feedback)

    def integral(self, feedback):
        return sum(self.feedback_hist[-10:]) + feedback

    def derivative(self, feedback):
        return (self.error(self.prev_feedback) - self.error(feedback)) / self.T

    def write(self):
        if len(self.feedback_hist)==0:
            return
        buf = ''
        buf+=str(self.feedback_hist[0])
        buf+=','
        for i in self.feedback_hist[1:-1]:
            buf+=str(i)+','
        if len(self.feedback_hist)>1:
            buf+=str(self.feedback_hist[-1])
        with open("f.hist", "w+") as f:
            f.write(buf)

    def acc(self):
        return sum(np.array(self.feedback_hist)==1)/float(len(self.feedback_hist))

class DarkfiTable:
    def __init__(self, airdrop, kp, ki, kd, target):
        self.Sigma=airdrop
        self.darkies = []
        KP=kp #0.48
        KI=ki #0.02
        KD=kd #0.2
        T=target
        TARGET=1
        self.pid = PID(KP, KI, KD, T, TARGET)

    def add_darkie(self, darkie):
        self.darkies+=[darkie]

    def background(self):
        feedback=0
        count = 0
        while count < RUNNING_TIME:
            f=self.pid.pid_clipped(feedback)
            tunning = Tunning(f, self.Sigma)
            winners = 0
            for i, darkie in enumerate(self.darkies):
                self.darkies[i].set_in(tunning)
                self.darkies[i].run()
                winners+=self.darkies[i].state.won
            if winners==1:
                self.Sigma+=REWARD
                for i, darkie in enumerate(self.darkies):
                    if self.darkies[i].state.won:
                        self.darkies[i].update_state()
            feedback=winners
            count+=1
        self.pid.write()
        return self.pid.acc()


AVG_LEN = 10
KP_STEP=0.1

KI_STEP=0.01
KI_SEARCH_START=0.4
KI_SEARCH_END=0.9

KD_STEP=0.1
KP_SEARCH_START=-1
KP_SEARCH_END=1

KD_SEARCH_START=-1
KD_SEARCH_END=1
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
                    for _ in range(0,NODES):
                        # equal airdrops
                        darkie = Darkie(AIRDROP/float(NODES))
                        dt.add_darkie(darkie)
                        darkie_acc = dt.background()
                        darkie_accs+=[darkie_acc]
                    acc = sum(darkie_accs)/float(len(darkie_accs))
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
