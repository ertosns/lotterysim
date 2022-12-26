from lottery import *

if __name__ == "__main__":
    dt  = DarkfiTable(10, 0.84, 0.849, 0.899, 1)
    darkies = [Darkie(2) for i in range(5)]
    for darkie in darkies:
        dt.add_darkie(darkie)
    dt.background()
