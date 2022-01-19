import sys
import logging
from timeit import default_timer as timer
from itertools import tee

import numpy as np

def coords2Index( x:float, y:float, h:float):
    return int(np.round(x/h)),int(np.round(y/h))

def index2Coords( ix:int, iy:int, h:float):
    return ix *h, iy*h
