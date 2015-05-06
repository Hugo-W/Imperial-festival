import time
import numpy as np
import matplotlib.pyplot as plt
import sys

plt.axis([0, 1000, 0, 1])
plt.ion()
plt.show()

for i in range(10):
    y = np.random.random()
    plt.scatter(i, y)
    plt.draw()
    time.sleep(0.001)
	
#input("PRESS ENTER TO QUIT.")
#sys.exit()