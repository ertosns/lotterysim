from utils import *
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
        self.pid.write("f"+str(self.id)+str("_")+str(self.stake)+".hist")

class PID:
    def __init__(self, kp=0, ki=0, kd=0, dt=1, target=1, Kc=0, Ti=0, Td=0, Ts=0, debug=False):
        self.Kp = kp # discrete pid kp
        self.Ki = ki # discrete pid ki
        self.Kd = kd # discrete pid kd
        self.T = dt # discrete pid frequency time.
        self.Ti = Ti # takahashi ti
        self.Td = Td # takahashi td
        self.Ts = Ts # takahashi ts
        self.Kc = Kc # takahashi kc
        self.target = target # pid set point
        self.prev_feedback = 0
        self.feedback_hist = [0, 0]
        self.f_hist = [0]
        self.error_hist = [0, 0]
        self.debug=debug

    def pid(self, feedback):
        ret =  (self.Kp * self.proportional(feedback)) + (self.Ki * self.integral(feedback)) + (self.Kd * self.derivative(feedback))
        self.feedback_hist+=[feedback]
        self.prev_feedback=feedback
        return ret

    def discrete_pid(self, feedback, debug=True):
        k1 = self.Kp + self.Ki + self.Kd
        k2 = -1 * self.Kp -2 * self.Kd
        k3 = self.Kd
        err = self.proportional(feedback)
        #if debug:
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

    def takahashi(self, feedback, debug=True):
        err = self.proportional(feedback)
        ret = self.f_hist[-1] + self.Kc * (self.feedback_hist[-1] - feedback + self.Ts * err/ self.Ti +  self.Td / self.Ts * (2*self.feedback_hist[-1] - feedback  - self.feedback_hist[-2]))
        self.error_hist+=[err]
        self.feedback_hist+=[feedback]
        return ret

    def pid_clipped(self, feedback, controller=CONTROLLER_TYPE_DISCRETE, debug=True):
        pid_value = None
        if controller == CONTROLLER_TYPE_TAKAHASHI:
            pid_value = self.takahashi(feedback, debug)
        elif controller == CONTROLLER_TYPE_DISCRETE:
            pid_value = self.discrete_pid(feedback, debug)
        else:
            pid_value = self.pid(feedback)


        if pid_value <= 0.0:
            pid_value = F_MIN
        elif pid_value >= 1:
            pid_value =  F_MAX
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

    def write(self, f_hist_file):
        if len(self.feedback_hist)==0:
            return
        buf = ''
        buf+=str(self.feedback_hist[0])
        buf+=','
        for i in self.feedback_hist[1:-1]:
            buf+=str(i)+','
        if len(self.feedback_hist)>1:
            buf+=str(self.feedback_hist[-1])
        with open(f_hist_file, "w+") as f:
            f.write(buf)

    def acc(self):
        return sum(np.array(self.feedback_hist)==1)/float(len(self.feedback_hist))

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
            self.leads_hist += [feedback]
            count += 1
        return sum([darkie.pid.acc() for darkie in self.darkies])/len(self.darkies)

    def write(self):
        for darkie in self.darkies:
            darkie.write()
        with open("leads.hist", 'w+') as file:
            buf = ''
            for leads in self.leads_hist:
                line=str(leads)+','
                buf+=line
            file.write(buf)
