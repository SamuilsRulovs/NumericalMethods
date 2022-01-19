import sys
import numpy as np
import matplotlib.pyplot as plt
from pointSelector import myPointSelector

def onSelect( vertices ):
    print(f'selected points : {vertices}')
    ## Uncomment below to disable the selector after 
    ## one point is selected.
    # pointSel.disconnect_events()
    # pointSel.set_visible(False)


fig = plt.figure()

ax = fig.add_subplot(1, 1, 1)

dimension = 4
resolution = 9

## Determine the distance between grid points
h = dimension /  ( resolution - 1. )

lengthUpperBound = dimension + h
myRange = np.arange(0,lengthUpperBound,h)

## Create grid points on the plot
grid_x = np.tile(myRange, resolution)
grid_y = np.repeat(myRange, resolution)
ax.scatter(grid_x, grid_y)

## Scatter the grid points
pointSel = myPointSelector(ax,h, onSelect)
plt.show()
