import random
import math
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

L = 28948022309329048855892746252171976963363056481941560715954676764349967630337
N_TERM = 2
AIRDROP = 1000
REWARD = 1
NODES = 100

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
    lottery_line = str(y)+","+str(T)+"\n"
    with open("/tmp/sim_lottery_history.log", "a+") as f:
        f.write(lottery_line)
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
        #print("total stake: {}".format(Sigma))
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
        self.f_hist = [0]
        self.error_hist = [0, 0]

    def pid(self, feedback):
        ret =  (self.Kp * self.proportional(feedback)) + (self.Ki * self.integral(feedback)) + (self.Kd * self.derivative(feedback))
        self.feedback_hist+=[feedback]
        self.prev_feedback=feedback
        return ret

    def discrete_pid(self, feedback):
        k1 = self.Kp + self.Ki + self.Kd
        k2 = -1 * self.Kp -2 * self.Kd
        k3 = self.Kd
        err = self.proportional(feedback)
        #print("pid::f-1: {}".format(self.f_hist[-1]))
        #print("pid::err: {}".format(err))
        #print("pid::err-1: {}".format(self.error_hist[-1]))
        #print("pid::err-2: {}".format(self.error_hist[-2]))
        #print("pid::k1: {}".format(k1))
        #print("pid::k2: {}".format(k2))
        #print("pid::k3: {}".format(k3))
        ret = self.f_hist[-1] + k1 * err + k2 * self.error_hist[-1] + k3 * self.error_hist[-2]

        self.error_hist+=[err]
        self.feedback_hist+=[feedback]
        return ret

    def pid_clipped(self, feedback):
        pid_value = self.discrete_pid(feedback)
        if pid_value <= 0.0:
            pid_value = 0.01
        elif pid_value >= 1:
            pid_value =  0.99
        if self.integral(feedback) == 0 and len(self.feedback_hist) >=3 and self.feedback_hist[-1] == 0 and self.feedback_hist[-2] == 0 and self.feedback_hist[-3] == 0:
            pid_value = math.pow(0.9, self.zero_lead_hist())
        self.f_hist+=[pid_value]
        return pid_value

    def zero_lead_hist(self):
        count = 0
        L = len(self.feedback_hist)
        for i in range(0,L):
            if self.feedback_hist[L-(i+1)]==0:
                count+=1
            else:
                return count
        return count

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
    def __init__(self, airdrop, kp, ki, kd, target, running_time):
        self.Sigma=airdrop
        self.darkies = []
        KP=kp #0.48
        KI=ki #0.02
        KD=kd #0.2
        T=1
        self.f_hist = []
        TARGET=target
        self.pid = PID(KP, KI, KD, T, TARGET)
        self.running_time=running_time

    def add_darkie(self, darkie):
        self.darkies+=[darkie]

    def background(self, discrete=True, rand_running_time=True):
        feedback=0
        count = 0
        # random running time
        RND_RUNNING_TIME = random.randint(1,self.running_time) if rand_running_time else self.running_time
        while count < RND_RUNNING_TIME:
            f=self.pid.pid_clipped(feedback)
            #print("f: {}".format(f))
            self.f_hist+=[f]
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

    def write(self):
        with open("f_val.hist", 'w+') as file:
            buf = ''
            for f in self.f_hist:
                line=str(f)+'\n'
                buf+=line
            file.write(buf)
