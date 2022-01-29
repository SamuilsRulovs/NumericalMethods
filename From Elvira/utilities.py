import sys
import logging
from timeit import default_timer as timer
from itertools import tee
import matplotlib.pyplot as plt
import numpy as np
from copy import copy

def coords2Index( x:float, y:float, h:float):
    return int(np.round(x/h)),int(np.round(y/h))

def index2Coords( ix:int, iy:int, h:float):
    return ix *h, iy*h


def SOR_solver2D(flagMtx, w_init,
               error = 0.1, max_iter=100,
               force = 0., omega_sor = 1.8):

    #flagMtx = np.pad(flagMtx,1)
    #w_init = np.pad(w_init,1)

    n = flagMtx.shape[0]#x coord
    m = flagMtx.shape[1]# y coord
    check_point = [False,  True,  True, False, False]
    #0: outside, 1: inside, 2: edge, 3: corner, 4: pillar
    w = w_init+0.0
    w_prev = w
    iter_num = 0
    diff = 1e6
    while iter_num<max_iter or diff>error:
        for ii in range(n):
            for jj in range(m):
                    if not check_point[flagMtx[ii,jj]]:
                        pass
                    else:
                        #ghost layer check
                        w_cent = w[ii,jj] #

                        if jj-1<=m:
                            a = w[ii, jj - 1]
                            if flagMtx[ii, jj - 1] == 0:
                                a = w_cent
                        else:
                            a = w_cent

                        # a = w[ii, jj - 1]
                        # if flagMtx[ii, jj - 1] == 0:
                        #     a = w_cent

                        if jj+1<=m:
                            b = w[ii, jj + 1]
                            if flagMtx[ii, jj + 1] == 0:
                                b = w_cent
                        else:
                            b = w_cent

                        # b = w[ii, jj + 1]
                        # if flagMtx[ii, jj + 1] == 0:
                        #     b = w_cent

                        if ii+1<=n:
                            c = w[ii + 1, jj]
                            if flagMtx[ii + 1, jj] == 0:
                                c = w_cent
                        else:
                            c = w_cent

                        # c = w[ii + 1, jj]
                        # if flagMtx[ii + 1, jj] == 0:
                        #     c = w_cent

                        if ii-1<=n:
                            d = w[ii - 1, jj]
                            if flagMtx[ii - 1, jj] == 0:
                                d = w_cent
                        else:
                            d = w_cent

                        # d = w[ii - 1, jj]
                        # if flagMtx[ii - 1, jj] == 0:
                        #     d = w_cent

                        w_tmp_gauss_seidal = (a + b + c + d + force) / 4

                        w_new_sor = (1-omega_sor)*w_cent + omega_sor*w_tmp_gauss_seidal
                        w[ii,jj] = w_new_sor
        iter_num = iter_num +1

        diff = np.max(w_prev-w)

        w_prev = w
    return w
# example
plt.figure()

width = 30
length = 100
flagMtx = np.ones((width, length))

flagMtx[1,:] = 3
flagMtx[-2,:] = 3
flagMtx[:,1] = 3
flagMtx[:, -2] = 3


flagMtx[0,:] = 0
flagMtx[-1,:] = 0
flagMtx[:,0] = 0
flagMtx[:, -1] = 0

flagMtx = flagMtx.astype(int)



flagMtx[20,20] = 4
flagMtx[10, 50] = 4

w_init = np.zeros_like(flagMtx)
w_init[20,20] = 20
w_init[10, 50] = 20

w_res = SOR_solver2D(flagMtx, w_init, force =+0.05)


fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, projection='3d')
X = np.arange(0, width, 1)
Y = np.arange(0, length, 1)
X, Y = np.meshgrid(X, Y)
Z = w_res.T

surf = ax.plot_surface(X, Y, Z)
plt.show()
