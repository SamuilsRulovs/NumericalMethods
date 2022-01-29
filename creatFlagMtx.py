import numpy as np
import utilities as uti
from Data import Data


class createFlagMtx:

    def __init__(self, data):
        self.data: Data = data

    def getBorderPolygon(self, canvas_h):
        print("getBorderPolygon opened")
        amountEdges = len(self.data.cornerIndex) - 1
        self.data.cornerCoords = [uti.index2Coords(index[0], index[1], canvas_h) for index in
                                  self.data.cornerIndex]
        u = 0
        while u < amountEdges:
            x1 = self.data.cornerCoords[u][0]
            y1 = self.data.cornerCoords[u][1]
            if u == amountEdges:
                x2 = self.data.cornerCoords[0][0]
                y2 = self.data.cornerCoords[0][1]
            else:
                x2 = self.data.cornerCoords[u + 1][0]
                y2 = self.data.cornerCoords[u + 1][1]
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            self.data.flagMtx[self.data.cornerIndex[u][0], self.data.cornerIndex[u][1]] = 3

            if abs(x2 - x1) < 0.0001:
                dx = -1.

            err = dx / 2

            if x1 < x2:
                sx = 1
            else:
                sx = -1
            if y1 < y2:
                sy = 1
            else:
                sy = -1
            continueLoop = True
            while continueLoop:
                x_index, y_index = uti.coords2Index(x1, y1, canvas_h)
                if self.data.flagMtx[x_index, y_index] == 1:
                    self.data.flagMtx[x_index, y_index] = 2
                if abs(x2 - x1) < 0.0001 and abs(y2 - y1) < 0.0001:
                    continueLoop = False
                if err >= 0:
                    x1 = x1 + sx * canvas_h
                    err = err - dy
                if err < 0:
                    y1 = y1 + sy * canvas_h
                    err = err + dx
            u += 1

    def callFloodFill(self, x, y) -> np.array:
        print("callFloodFill opened")
        if self.data.flagMtx[x, y] == 1:
            self.data.flagMtx[x, y] = 0
            try:
                self.callFloodFill(x, y + 1)
            except IndexError:
                pass
            try:
                self.callFloodFill(x, y - 1)
            except IndexError:
                pass
            try:
                self.callFloodFill(x + 1, y)
            except IndexError:
                pass
            try:
                self.callFloodFill(x - 1, y)
            except IndexError:
                pass
