import matplotlib.pyplot as plt

with open('f.hist', 'r') as f:
    buff = f.read()
    hist = buff.split(',')
    plt.plot(hist)

plt.savefig("hist.png")
