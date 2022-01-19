import sys
import numpy as np
import matplotlib.pyplot as plt
from polygonSelector import myPolygonSelector

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

## An alternative way to do this , 
# xx,yy = np.meshgrid(myRange,myRange)
# ax.plot(xx,yy,marker='.',color='k',linestyle='none')

## Scatter the grid points
polygonSel = myPolygonSelector(ax,h, lambda vertices : print(f'corner of the polygon : {vertices}'))
plt.show()
