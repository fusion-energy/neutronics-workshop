
import adaptive

def ring(xy, wait=True):
    import numpy as np
    from time import sleep
    from random import random
    if wait:
        sleep(random()/10)
    x, y = xy
    a = 0.2
    return x + np.exp(-(x**2 + y**2 - 0.75**2)**2/a**4)

learner = adaptive.Learner2D(ring, bounds=[(-1, 1), (-1, 1)])