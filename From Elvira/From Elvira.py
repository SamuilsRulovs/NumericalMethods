import sys
import logging
from timeit import default_timer as timer
from itertools import tee
import matplotlib.pyplot as plt
import numpy as np
from copy import copy

def SOR_solver2D(flagMtx, w_init,
               error = 0.1, max_iter=100,
               force = 0., omega_sor = 1.8):

    n = flagMtx.shape[0]#x coord
    m = flagMtx.shape[1]# y coord
    check_point = [False,  True,  True, True, False]
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

                        if jj+1<=m:
                            b = w[ii, jj + 1]
                            if flagMtx[ii, jj + 1] == 0:
                                b = w_cent
                        else:
                            b = w_cent

                        if ii+1<=n:
                            c = w[ii + 1, jj]
                            if flagMtx[ii + 1, jj] == 0:
                                c = w_cent
                        else:
                            c = w_cent

                        if ii-1<=n:
                            d = w[ii - 1, jj]
                            if flagMtx[ii - 1, jj] == 0:
                                d = w_cent
                        else:
                            d = w_cent

                        w_tmp_gauss_seidal = (a + b + c + d + force) / 4

                        w_new_sor = (1-omega_sor)*w_cent + omega_sor*w_tmp_gauss_seidal
                        w[ii,jj] = w_new_sor
        iter_num = iter_num +1

        diff = np.max(w_prev-w)

        w_prev = w
    return w