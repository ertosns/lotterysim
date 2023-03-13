from utils import *
from threading import Thread

class Darkie(Thread):
    def __init__(self, airdrop):
        Thread.__init__(self)
        self.stake = Num(airdrop)
        self.finalized_stake = Num(airdrop) # after fork finalization
        self.Sigma = None
        self.feedback = None
        self.f = None
        self.won=False

    def clone(self):
        return Darkie(self.finalized_stake)

    def set_sigma_feedback(self, sigma, feedback, f):
        self.Sigma = Num(sigma)
        self.feedback = Num(feedback)
        self.f = Num(f)

    def run(self):
        k=N_TERM
        def target(tune_parameter, stake):
            x = Num(1)-tune_parameter
            c = x.ln()
            sigmas = [(c/((self.Sigma+EPSILON)**i) * (L/fact(i))) for i in range(1, k+1)]
            scaled_target = approx_target_in_zk(sigmas, stake) + BASE_L
            return scaled_target
        T = target(self.f, self.finalized_stake)
        self.won = lottery(T)

    def update_stake(self):
        self.stake+=REWARD

    def finalize_stake(self):
        if self.won:
            self.finalized_stake = self.stake
        else:
            self.stake = self.finalized_stake
