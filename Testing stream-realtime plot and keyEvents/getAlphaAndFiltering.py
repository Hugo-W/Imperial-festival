# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 

from emokit.emotiv import Emotiv
import platform
if platform.system() == "Windows":
    import socket  # Needed to prevent gevent crashing on Windows. (surfly / gevent issue #459)
import gevent
import sys

import numpy as np
from scipy.signal import butter, lfilter

 
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a
    
def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def getAlphaPower(buff, Ts = 1/128):
    N = len(buff)
    freq = np.fft.fftfreq(N,Ts)
    Power = np.abs(np.fft(buff))**2
    spectrum = zip(freq,Power)
    alphalist = []
    for (f,S) in spectrum:
        if f>=8 and f<=12:
            alphalist.append(S)
    alpha = np.mean(alphalist)

    return alpha
    

if __name__ == "__main__":
    headset = Emotiv()
    routine = gevent.spawn(headset.setup)
    gevent.sleep(0)
    try:
        while True:
            buffin = []
            for i in xrange(128):
                packet = headset.dequeue()
                buffin.append(packet.sensors['F3']['value'])
                #print packet.gyro_x, packet.gyro_y, packet.battery
                gevent.sleep(0)
            alpha = getAlphaPower(buffin)
            print alpha
    except KeyboardInterrupt:
        headset.running = False
        headset.close()
        gevent.kill(routine, KeyboardInterrupt)
    finally:
        headset.close()
        gevent.kill(routine)
    sys.exit()