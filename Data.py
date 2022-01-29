import numpy as np

class Data:

    def __init__(self, resolution):
        self.resolution = resolution
        self.wMtx = np.zeros((resolution, resolution)).astype(float)
        self.flagMtx = np.ones((resolution, resolution)).astype(int)
        self.pillarCoords = []
        self.pillarIndex = []
        self.cornerCoords = []
        self.cornerIndex = []
