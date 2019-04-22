import numpy as np
import matplotlib.pyplot as plt

phi = np.random.randn(20, 20) # initial value for phi
F = +0.01 *np.ones_like(phi) # some function
phi[5:10,5:10]=0
F[5:10,5:10]=0
dt = 1
it = 100
plt.ion()
for i in range(it):
     dphi = np.gradient(phi)
     dphi_norm = 0.5*(np.sqrt(np.sum(dphi[0]**2, axis=0))+np.sqrt(np.sum(dphi[1]**2, axis=0)))

     phi = phi + dt * F * dphi_norm

     # plot the zero level curve of phi
     plt.clf()
     plt.contour(phi, 0)
     plt.show()
     plt.pause(0.5)
