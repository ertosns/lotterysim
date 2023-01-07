import matplotlib.pyplot as plt
import numpy as np

with open('f.hist', 'r') as f:
    buff = f.read()
    hist = buff.split(',')
    plt.plot(hist)
    freq = sum(np.array([float(i) for i in hist])==1)/len(hist)
    print("freq: {}".format(freq))

plt.savefig("hist.png")
