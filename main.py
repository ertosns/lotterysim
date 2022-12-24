import random
import math
import numpy as np
import matplotlib.pyplot as plt

L = 28948022309329048855892746252171976963363056481941560715954676764349967630337
N_TERM = 2
AIRDROP = 10
REWARD = 3
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
    print("y: ", y)
    print("T: ", T)
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
        print("f: ", f)
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


class DarkfiTable:
    def __init__(self, airdrop):
        self.Sigma=airdrop
        self.darkies = []
        KP=0.48
        KI=0.02
        KD=0.2
        T=1
        TARGET=1
        self.pid = PID(KP, KI, KD, T, TARGET)

    def add_darkie(self, darkie):
        self.darkies+=[darkie]

    def background(self):
        feedback=0
        count = 0
        while count < 50:
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

if __name__ == "__main__":
    dt = DarkfiTable(AIRDROP)
    for _ in range(0,NODES):
        # equal airdrops
        darkie = Darkie(AIRDROP/float(NODES))
        dt.add_darkie(darkie)
    dt.background()
