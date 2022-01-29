import sys

sys.path.append("..")
import numpy as np
import matplotlib.pyplot as plt
import utilities as uti
from polygonSelector import myPolygonSelector


### your implementation
def getBorderPolygon(flagMtx: np.array, cornerIndex: list) -> np.array:
    amountEdges = len(cornerIndex) - 1
    cornerCoords = []
    i = 0
    while i < len(cornerIndex):
        cornerCoords.append(uti.index2Coords(cornerIndex[i][0], cornerIndex[i][1], h))
        i += 1
    u = 0
    while u < amountEdges:
        x1 = cornerCoords[u][0]
        y1 = cornerCoords[u][1]
        if u == amountEdges:
            x2 = cornerCoords[0][0]
            y2 = cornerCoords[0][1]
        else:
            x2 = cornerCoords[u + 1][0]
            y2 = cornerCoords[u + 1][1]
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        flagMtx[cornerIndex[u][0], cornerIndex[u][1]] = 3
        if abs(x2 - x1) < 0.0001:
            dx = -1.
        err = dx / 2
        if x1 < x2:
            sx = 1.
        else:
            sx = -1.
        if y1 < y2:
            sy = 1.
        else:
            sy = -1.
        continueLoop = True
        while continueLoop:
            x_index, y_index = uti.coords2Index(x1, y1, h)
            if flagMtx[x_index, y_index] == 1:
                flagMtx[x_index, y_index] = 2
            # if [x1, y1] == [x2, y2]:
            if abs(x2-x1) < 0.0001 and abs(y2-y1) < 0.0001:
                continueLoop = False
            if err >= 0.:
                x1 = x1 + sx * h
                err = err - dy
            if err < 0.:
                y1 = y1 + sy * h
                err = err + dx
        u += 1
    return flagMtx


### your implementation
def callFloodFill(flagMtx: np.array, x, y) -> np.array:
    if flagMtx[x, y] == 1:
        flagMtx[x, y] = 0
        callFloodFill(flagMtx, x, y + 1)
        callFloodFill(flagMtx, x, y - 1)
        callFloodFill(flagMtx, x + 1, y)
        callFloodFill(flagMtx, x - 1, y)
    return flagMtx


corners = []
resolution = 15
dimension = 6
h = dimension / (resolution - 1.)
fig = plt.figure()
ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(1, 2, 2)
lengthUpperBound = dimension + h - 1e-15
myRange = np.arange(0, lengthUpperBound, h)
w = []

## Create grid points on the plot
grid_x = np.tile(myRange, resolution)
grid_y = np.repeat(myRange, resolution)
ax1.scatter(grid_x, grid_y)
flagMtx = np.ones((resolution, resolution))
flagMtx = flagMtx.astype(int)


# lambda function that will be called with the corners of the polygon drawn
def lam(vert):
    corners = vert
    corners.append(corners[0])
    cornerIndex = [uti.coords2Index(v[0], v[1], h) for v in corners]

    ## get a matrix with 2:edge, 3: corner
    flag = getBorderPolygon(flagMtx, cornerIndex)
    flag = callFloodFill(flag, 0, 0)

    ## rotate to make the image align 
    ax2.imshow(np.array(np.rot90(flag)))
    ## draw the result of your implementation
    fig.canvas.draw()


polygonSel = myPolygonSelector(ax1, h, lam)

plt.show()
