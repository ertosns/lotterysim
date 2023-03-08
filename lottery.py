import matplotlib.pyplot as plt
from tqdm import tqdm
from darkie import *
import time
from datetime import timedelta
from pid import PID

class DarkfiTable:
    def __init__(self, airdrop, running_time, controller_type=CONTROLLER_TYPE_DISCRETE, kp=0, ki=0, kd=0, dt=1, target=1, kc=0, ti=0, td=0, ts=0):
        self.Sigma=airdrop
        self.darkies = []
        self.running_time=running_time
        self.start_time=None
        self.end_time=None
        self.pid = None
        self.pid = PID(kp=kp, ki=ki, kd=kd, dt=dt, target=target, Kc=kc, Ti=ti, Td=td, Ts=ts)
        self.controller_type=controller_type

    def add_darkie(self, darkie):
        self.darkies+=[darkie]

    def background(self, rand_running_time=True, debug=True):
        self.start_time=time.time()
        feedback=0 # number leads in previous slot
        count = 0
        # random running time
        rand_running_time = random.randint(1,self.running_time) if rand_running_time else self.running_time
        self.running_time = rand_running_time
        if rand_running_time:
            print("random running time: {}".format(self.running_time))
        spinoffs = []
        joins = []
        finalizations = []
        restarts = []
        pids = []
        length = len(self.darkies)
        while count < self.running_time:
            winners = 0

            ###
            # controller
            ###
            pid_start = time.time()
            f = self.pid.pid_clipped(feedback, self.controller_type, debug)
            pids += [time.time() - pid_start]

            ###
            # spin off threads
            ###
            spin_off_start = time.time()
            for i in range(length):
                self.darkies[i].set_sigma_feedback(self.Sigma, feedback, f)
                self.darkies[i].start()
            spinoffs += [time.time() - spin_off_start]

            ###
            # join threads,
            ###
            join_start = time.time()
            for i in range(length):
                self.darkies[i].join()
                darkie_won = self.darkies[i].won
                if darkie_won:
                    self.darkies[i].update_stake()
                    winners+=darkie_won
            joins += [time.time() - join_start]

            ###
            # resolve finalization:
            # reset stakes when finalization is resolved.
            ###
            finalization_start = time.time()
            if winners==1:
                self.Sigma+=REWARD
                for i in range(length):
                    self.darkies[i].finalize_stake()
            feedback = winners
            assert (feedback <= len(self.darkies))
            count += 1
            finalizations += [time.time() - finalization_start]

            ###
            # restart thread
            ###
            restart_start = time.time()
            for i in range(length):
                self.darkies[i] = self.darkies[i].clone()
            restarts += [time.time() - restart_start]

        self.end_time=time.time()
        if debug:
            print("pid per slot: {}.".format(str(timedelta(seconds=sum(pids)/len(pids)))))
            print("spin off per slot: {}.".format(str(timedelta(seconds=sum(spinoffs)/len(spinoffs)))))
            print("thread work per slot: {}.".format(str(timedelta(seconds=sum(joins)/len(joins)))))
            print("finalization per slot: {}.".format(str(timedelta(seconds=sum(finalizations)/len(finalizations)))))
            print("restart per slot: {}.".format(str(timedelta(seconds=sum(restarts)/len(restarts)))))
        return self.pid.acc()

    def write(self):
        elapsed=self.end_time-self.start_time
        print("total time: {}, slot time: {}".format(str(timedelta(seconds=elapsed)), str(timedelta(seconds=elapsed/self.running_time))))
        self.pid.write()
