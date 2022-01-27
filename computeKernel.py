from Data import Data
import numpy as np


class ComputeKernel:

    def __init__(self, data):
        self.data: Data = data

    def compute(self):
        error = 0.1
        force = 0.0
        omega_sor = 1.8
        n_max = 1000
        n = self.data.flagMtx.shape[0]  # x coord
        m = self.data.flagMtx.shape[1]  # y coord
        check_point = [False, True, True, False, False]
        # 0: outside, 1: inside, 2: edge, 3: corner, 4: pillar
        w_matrix = self.data.wMtx + 0.0
        w_prev = w_matrix
        iter_num = 0
        diff = 1e6
        while iter_num < n_max or diff > error:
            for ii in range(n):
                for jj in range(m):
                    if not check_point[self.data.flagMtx[ii, jj]]:
                        pass
                    else:
                        # ghost layer check
                        w_cent = w_matrix[ii, jj]  #

                        if jj - 1 <= m:
                            a = w_matrix[ii, jj - 1]
                            if self.data.flagMtx[ii, jj - 1] == 0:
                                a = w_cent
                        else:
                            a = w_cent

                        if jj + 1 <= m:
                            b = w_matrix[ii, jj + 1]
                            if self.data.flagMtx[ii, jj + 1] == 0:
                                b = w_cent
                        else:
                            b = w_cent

                        if ii + 1 <= n:
                            c = w_matrix[ii + 1, jj]
                            if self.data.flagMtx[ii + 1, jj] == 0:
                                c = w_cent
                        else:
                            c = w_cent

                        if ii - 1 <= n:
                            d = w_matrix[ii - 1, jj]
                            if self.data.flagMtx[ii - 1, jj] == 0:
                                d = w_cent
                        else:
                            d = w_cent

                        w_tmp_gauss_seidal = (a + b + c + d + force) / 4

                        w_new_sor = (1 - omega_sor) * w_cent + omega_sor * w_tmp_gauss_seidal
                        w_matrix[ii, jj] = w_new_sor
            iter_num = iter_num + 1

            diff = np.max(w_prev - w_matrix)

            w_prev = w_matrix
        self.data.wMtx = w_matrix

    def postprocess(self):
        print("postprocess")
        mesh_x = np.arange(0, self.data.resolution, 1)
        mesh_y = np.arange(0, self.data.resolution, 1)
        mesh_x, mesh_y = np.meshgrid(mesh_x, mesh_y)
        mesh_z = self.data.wMtx.T
        n = mesh_z.shape[0]
        m = mesh_z.shape[1]
        for i in range(0, n):
            for j in range(0, m):
                if mesh_z[i, j] == 0.0:
                    mesh_z[i, j] = None
        return mesh_x, mesh_y, mesh_z
