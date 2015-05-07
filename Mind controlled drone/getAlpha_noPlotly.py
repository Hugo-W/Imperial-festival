# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 

from emokit.emotiv import Emotiv
import platform
if platform.system() == "Windows":
    import socket  # Needed to prevent gevent crashing on Windows. (surfly / gevent issue #459) / UDP Client requires
import gevent
import sys

import time

import numpy as np
import scipy

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


def getAlphaPower(buff, ffttype,Ts = 1./128):
    N = len(buff)
    freq = np.fft.fftfreq(N,Ts)     # Creating a vector (np.array) for all frequencies (Nyquist in the middle); N number of points, Ts sampling time
    if ffttype == 'square':
        Power = 2.*np.abs(np.fft.fft(buff))**2/N**2 # squared
    else:
        Power = 2.*np.abs(np.fft.fft(buff))/N       # Not squared
    spectrum = zip(freq,Power)      #This is a list of "tuples" (freq, value)...
    alphalist = []                  # Taking the power of alpha rhythms into this list
    for (f,S) in spectrum:
        if f>=8 and f<=12:          #You cannot do more basic filtering...
            alphalist.append(S)
    alpha = np.amax(alphalist)      #Averaging... (we could take the max or the norm )
    if ffttype=='log': alpha = 10.*np.log10(alpha)     # Log/Linear
    return alpha
    

if __name__ == "__main__":
    N = 256
    ffttype = 'log'
    param = dict({'square':[10.,100.] , 'log':[6.,30.], 'abs':[5.,20.]})  # [min value (eyes open), max (eyes closed)]
    buffin = RingBuffer(N)
    headset = Emotiv()
    routine = gevent.spawn(headset.setup)
    gevent.sleep(0)
    win = scipy.hamming(N)
    normalizing = np.sum(np.multiply(win,np.ones(N)*1./N))
    #win = np.ones(N)
    t0 = time.clock()
    told = t0
    # Jin UDP Client
    host = '127.0.0.1'
    port = 10000  #int(raw_input("Enter Listening Port:"))

    # Create a UDP socket
    try:
        print 'Init UDP Client: IP: %s Port: %s...' % (host,port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print 'Client init complete'
    except socket.error, msg:
        print 'Client init failed. Error Code: ' + str(msg[0]) + ' Message: ' + msg[1]

    try:
        temp_buffer = []
        for i in xrange(N):
            packet = headset.dequeue()
            temp_buffer.append(packet.sensors['F3']['value']) 
            gevent.sleep(0)
        buffin.extend(temp_buffer)
        #print getAlphaPower(np.multiply(win,buffin.get())) # hamming window to sharpen fft
        while True:            
            packet = headset.dequeue()
            buffin.extend(packet.sensors['O1']['value'])
            #print packet.gyro_x, packet.gyro_y, packet.battery
            gevent.sleep(0)
            alpha = getAlphaPower(np.multiply(win,buffin.get())/normalizing,ffttype)  # hamming window to sharpen fft
            #print alpha
            
            # Jin UDP Client
            try:
                alphaScale = (alpha - param[ffttype][0])/(param[ffttype][1]-param[ffttype][0])
                #print alphaScale
                alphaScale = max(0, min(alphaScale,1))    # clamp alpha
                #if np.mod(np.trunc(1000*(time.clock()-t0)),5.0)<1:
                if time.clock()-told>0.015:
                    told = time.clock()
                    sock.sendto(str(alphaScale), (host, port))
                    sock.sendto(str(alphaScale), (host, port + 1))
            except socket.error, msg:
                print 'Error Code: ' + str(msg[0]) + ' Message: ' + msg[1]
                
    except KeyboardInterrupt:
        headset.running = False
        headset.close()
        gevent.kill(routine, KeyboardInterrupt)
    finally:
        headset.close()
        gevent.kill(routine)
    
    # Jin UDP Client
    print >>sys.stderr, 'Closing socket'
    sock.close()
    sys.exit()