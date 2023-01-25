from utils import *
from pid import PID
import matplotlib.pyplot as plt
from tqdm import tqdm

class State:
    def __init__(self, f, T, won):
        self.f=f
        self.T=T
        self.won=won

class Darkie:
    def __init__(self, controller, airdrop, id=0, kp=0, ki=0, kd=0, dt=1, target=1, kc=0, ti=0, td=0, ts=0, debug=True):
        self.controller = controller
        self.finalized_stake = airdrop
        self.id = id
        self.stake = airdrop
        self.state = None
        self.debug = debug
        self.f_hist = []
        self.pid = PID(kp=kp, ki=ki, kd=kd, dt=dt, target=target, Kc=kc, Ti=ti, Td=td, Ts=ts)

    def run(self, feedback, Sigma):
        f = self.pid.pid_clipped(feedback, self.controller, self.debug)
        self.f_hist += [f]
        k=N_TERM
        def target(tune_parameter, stake):
            x = 1-tune_parameter
            c = math.log(x)
            sigmas = [int((c/(Sigma+EPSILON))**i * (L/fact(i))) for i in range(1, k+1)]
            scaled_target = approx_target_in_zk(sigmas, stake) + L*F_MIN
            return scaled_target
        #T_min = target(0.99, self.stake)
        #T_max = target(0.01, self.stake)
        #T_scaled = target(f, self.stake)
        #T = (T_scaled - T_min ) / ((T_max - T_min)/L)
        #print("T min {}".format(T_min))
        #print("T max {}".format(T_max))        
        #print("T scaled {}".format(T_scaled))
        #print("T {}".format(T))
        T = target(f, self.stake)
        is_lead = lottery(T)
        self.state = State(f, T, is_lead)

    def update_stake(self):
        self.stake+=REWARD

    def finalize_stake(self):
        self.stake=self.finalized_stake
        self.stake+=REWARD
        self.finalized_stake=self.stake

    def write(self):
        f_val_file = "f"+str(self.id)+str("_")+str(self.stake)+".hist"
        lead_file = "leads"+str(self.id)+str("_")+str(self.stake)+".hist"
        self.pid.write(lead_file, f_val_file)


class DarkfiTable:
    def __init__(self, airdrop, running_time):
        self.Sigma=airdrop
        self.darkies = []
        self.leads_hist = []
        self.running_time=running_time

    def add_darkie(self, darkie):
        self.darkies+=[darkie]

    def background(self, rand_running_time=True, debug=True):
        feedback=0
        count = 0
        # random running time
        RND_RUNNING_TIME = random.randint(1,self.running_time) if rand_running_time else self.running_time
        if rand_running_time:
            print("random running time: {}".format(RND_RUNNING_TIME))
        while count < RND_RUNNING_TIME:
            winners = 0
            for i, darkie in enumerate(self.darkies):
                self.darkies[i].run(feedback, self.Sigma)
                darkie_won = self.darkies[i].state.won
                if darkie_won:
                    self.darkies[i].update_stake()
                    winners+=darkie_won
            
            if winners==1:
                self.Sigma+=REWARD
                for i, darkie in enumerate(self.darkies):
                    if self.darkies[i].state.won:
                        self.darkies[i].finalize_stake()
            feedback = winners
            assert (feedback <= len(self.darkies))
            self.leads_hist += [feedback]
            count += 1
        return sum([darkie.pid.acc() for darkie in self.darkies])/len(self.darkies)

    def write(self):
        for darkie in self.darkies:
            darkie.write()
