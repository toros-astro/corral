import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_context(context='paper', font_scale=1.8)

mse = np.arange(40)
f20 = np.exp(mse/20.)
f13 = np.exp(mse/13.)
f10 = np.exp(mse/10.)
f5 = np.exp(mse/5.)

gf10 = 2./(1+f10)
gf13 = 2./(1+f13)
gf5 = 2./(1+f5)
gf20 = 2./(1+f20)


plt.rc('text', usetex=True)
plt.rc('font', family='serif', size=20)

plt.plot(mse, gf20, 'r-.', label=r'$\tau=20$')
plt.plot(mse, gf13, 'b', label=r'$\tau=13$')
plt.plot(mse, gf10, 'g:', label=r'$\tau=10$')
plt.plot(mse, gf5, 'y--', label=r'$\tau=5$')
plt.ylabel(r'$2 \times [1+exp(MSE/\tau)]^{-1}$')
plt.xlabel('MSE Style errors')
plt.legend(loc=1)
plt.show()

