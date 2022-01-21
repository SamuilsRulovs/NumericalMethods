import sys

sys.path.append("..")
import numpy as np
import matplotlib.pyplot as plt
import utilities as uti
from polygonSelector import myPolygonSelector


### your implementation
def getBorderPolygon(flagMtx: np.array, cornerIndex: list) -> np.array:
    pass


### your implementation
def callFloodFill(flagMtx: np.array) -> np.array:
    pass


corners = []
resolution = 15
dimension = 6
h = dimension / (resolution - 1.)
fig = plt.figure()
ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(1, 2, 2)
lengthUpperBound = dimension + h - 1e-15
myRange = np.arange(0, lengthUpperBound, h)

## Create grid points on the plot
grid_x = np.tile(myRange, resolution)
grid_y = np.repeat(myRange, resolution)
ax1.scatter(grid_x, grid_y)
flagMtx = np.ones((resolution, resolution))


# lambda function that will be called with the corners of the polygon drawn
def lam(vert):
    corners = vert
    corners.append(corners[0])
    cornerIndex = [uti.coords2Index(v[0], v[1], h) for v in corners]

    ## get a matrix with 2:edge, 3: corner
    flag = getBorderPolygon(flagMtx, cornerIndex)
    flag = callFloodFill(flag)

    ## rotate to make the image align 
    ax2.imshow(np.array(np.rot90(flag)))
    ## draw the result of your implementation
    fig.canvas.draw()


polygonSel = myPolygonSelector(ax1, h, lam)

plt.show()
