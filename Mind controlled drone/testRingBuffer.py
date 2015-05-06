import numpy as np
from scipy.fftpack import fft
import matplotlib.pyplot as plt
#from collections import deque


class RingBuffer():
    "A 1D ring buffer using numpy arrays"
    def __init__(self, length):
        self.data = np.zeros(length, dtype='f')
        self.index = 0

    def extend(self, x):
        "adds array x to ring buffer"
        x_index = (self.index + np.arange(x.size)) % self.data.size
        self.data[x_index] = x
        self.index = x_index[-1] + 1

    def get(self):
        "Returns the first-in-first-out data in the ring buffer"
        idx = (self.index + np.arange(self.data.size)) %self.data.size
        return self.data[idx]
        
    def __len__(self):
        return np.size(self.data)

N = 128
T = 1.0 / 800.0
x = np.linspace(0.0, N*T, N)
y = RingBuffer(N)
y.extend(np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x))

plt.plot(x,y.get())
plt.grid()
plt.show()

yf = fft(y.get())
xf = np.linspace(0.0, 1.0/(1.0*T), N)

plt.plot(xf, 2.0/N * np.abs(yf[0:N]))
plt.grid()
plt.show()


yfnew=yf

for tt in range(0,12800):

	old=y.get()[0]

	#plt.plot(xf, 2.0/N * np.abs(yf[0:N]))
	#plt.grid()
	#plt.show()

	qq=np.sin(100 * 2.0*np.pi*x[np.mod(tt,N)])

	y.extend(qq)



	change = yfnew + (qq-old)*np.ones(N)

	aa = np.linspace(0,2j*np.pi,num=N,endpoint=False)
	phasediff = np.exp(aa)

	yfnew = change*phasediff

plt.plot(x,y.get())
plt.grid()
plt.show()

plt.plot(xf, 2.0/N * np.abs(yfnew[0:N]))
plt.grid()
plt.show()
