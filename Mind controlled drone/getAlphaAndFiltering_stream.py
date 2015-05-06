# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 

from emokit.emotiv import Emotiv
import platform
if platform.system() == "Windows":
    import socket  # Needed to prevent gevent crashing on Windows. (surfly / gevent issue #459)
import gevent
import sys

import time
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import Stream, Scatter, Data, Layout, Figure

import numpy as np
from scipy.signal import butter, lfilter

class RingBuffer():
    "A 1D ring buffer using numpy arrays"
    def __init__(self, length):
        self.data = np.zeros(length, dtype='f')
        self.index = 0

    def extend(self, x):
        "adds array x to ring buffer"
        if not isinstance(x,np.ndarray): x = np.array(x)
        x_index = (self.index + np.arange(x.size)) % self.data.size
        self.data[x_index] = x
        self.index = x_index[-1] + 1

    def get(self):
        "Returns the first-in-first-out data in the ring buffer"
        idx = (self.index + np.arange(self.data.size)) %self.data.size
        return self.data[idx]

    def __len__(self):
        return np.size(self.data)
        
 #These two following functions do bandpass filtering: (the first one calculate the coeff, the second filter data)
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a
    #But for online filtering, using just the coefficients a,b might be enough...
def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def getAlphaPower(buff, Ts = 1./128):
    N = len(buff)
    freq = np.fft.fftfreq(N,Ts)     # Creating a vector (np.array) for all frequencies (Nyquist in the middle); N number of points, Ts sampling time
    Power = np.abs(np.fft.fft(buff))**2
    spectrum = zip(freq,Power)      #This is a list of "tuples" (freq, value)...
    alphalist = []                  # Taking the power of alpha rhythms into this list
    for (f,S) in spectrum:
        if f>=8 and f<=12:          #You cannot do more basic filtering...
            alphalist.append(S)
    alpha = np.mean(alphalist)      #Averaging... (we could take the max or the norm )

    return alpha
    

if __name__ == "__main__":
    N = 128
    buffin = RingBuffer(N)
    headset = Emotiv()
    routine = gevent.spawn(headset.setup)
    gevent.sleep(0)
    
    #PLOTLY:
    stream_ids = tls.get_credentials_file()['stream_ids']
    stream_id = stream_ids[3]
    stream = Stream(token = stream_id, maxpoints = 50)
    
    #Create a trace with embedded stream id object:
    trace1 = Scatter(x = [], y = [], mode = 'lines+markers', stream = stream)
    data = Data([trace1])
    
    #Layout dictionnary:
    layout = Layout(title = 'Alpha power (dB/Hz)')
    #Create Figure object:
    fig = Figure(data = data, layout = layout)
    
    unique_url = py.plot(fig, filename='Streaming alpha waves')
    
    #Create instance of Stream LINK object, using same stream_id token:
    s = py.Stream(stream_id)
    s.open()
    t0 = time.clock()
    try:
        temp_buffer = []
        for i in xrange(N):
            packet = headset.dequeue()
            temp_buffer.append(packet.sensors['F3']['value']) 
            gevent.sleep(0)
        buffin.extend(temp_buffer)
        print getAlphaPower(buffin.get())
        while True:            
            packet = headset.dequeue()
            buffin.extend(packet.sensors['F3']['value'])
            #print packet.gyro_x, packet.gyro_y, packet.battery
            gevent.sleep(0)
            alpha = getAlphaPower(buffin.get())
            #print alpha
            if np.mod(np.trunc(1000*(time.clock()-t0)),80.0)<3: s.write(dict(x = time.clock()-t0, y = 10.*np.log10(alpha)))
    except KeyboardInterrupt:
        headset.running = False
        headset.close()
        gevent.kill(routine, KeyboardInterrupt)
    finally:
        headset.close()
        gevent.kill(routine)
        s.close()
    sys.exit()