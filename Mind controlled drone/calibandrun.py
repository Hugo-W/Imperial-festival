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
from scipy.fftpack import fft
from time import time, clock, sleep



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
    

def updateFFT(oldPoint, newPoint, oldFFT, pd):
    change = oldFFT + (newPoint - oldPoint) * np.ones(len(oldFFT))
    return change*pd

def getAlphaFromFT(yf, window):         # Either Max/ or mean
    #return np.mean(np.abs(yf[window]**2))  / len(yf)    # square version
    return np.mean(np.log10(np.abs(yf[window]/len(yf))))       # log power
    #return np.mean(np.abs(yf[window]))/ np.sqrt(len(yf))     # spectrum absolute

    ###HI HUGO! IT SEEMS LIKE NORMALISING THESE ALPHA VALUES BY sqrt(N) GIVES DECENT RESULTS... I HAVE NO IDEA WHY

#sensornames = ['F3','FC5','AF3','F7','T7','P7','O1','O2','P8','T8','F8','AF4','FC6','F4']

sensornames = ['O1','P7','P8']

# !!!!! Be careful: P7 used instead of P7 (names in variables...)

N = 128 # size of ringbuffer
Ncalib = 2048

alpha_min = 8 # Hz
alpha_max = 13 # Hz
sf = 128.0 # sampling freq, Hz

totaltime = 90 #sec of controlli ng drone

aa = np.linspace(0,2j*np.pi,num=N,endpoint=False)
phasediff = np.exp(aa)

alpha_range = range(np.int(np.ceil(alpha_min*N/sf)),np.int(np.floor(alpha_max*N/sf)))
alpha_range_calib = range(np.int(np.ceil(alpha_min*Ncalib/sf)),np.int(np.floor(alpha_max*Ncalib/sf)))


if __name__ == "__main__":
    headset = Emotiv()
    routine = gevent.spawn(headset.setup)
    gevent.sleep(0)
    
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
        #CALIB OPEN
        print "PLEASE OPEN YOUR EYES AND TRY TO KEEP STILL" 
        O1calib=[]
        P7calib=[]
        P8calib=[]
        for i in range(Ncalib):
            packet = headset.dequeue()                

            O1calib.append(packet.sensors['O1']['value'])
            P7calib.append(packet.sensors['P7']['value'])
            P8calib.append(packet.sensors['P8']['value'])
                

               
            gevent.sleep(0)

        alphaO1o = getAlphaFromFT(fft(O1calib), alpha_range_calib)
        alphaP7o = getAlphaFromFT(fft(P7calib),alpha_range_calib)
        alphaP8o = getAlphaFromFT(fft(P8calib),alpha_range_calib)
        
        print "Calibration eyes open: ", (alphaO1o,alphaP7o,alphaP8o)
        
        #CALIB CLOSED

        print "NOW CLOSE YOUR EYES" 
        sleep(3)
        O1calib=[]
        P7calib=[]
        P8calib=[]
        for i in range(Ncalib):
            packet = headset.dequeue()                

            O1calib.append(packet.sensors['O1']['value'])
            P7calib.append(packet.sensors['P7']['value'])
            P8calib.append(packet.sensors['P8']['value'])
                

               
            gevent.sleep(0)


        alphaO1c = getAlphaFromFT(fft(O1calib),alpha_range_calib)
        alphaP7c = getAlphaFromFT(fft(P7calib),alpha_range_calib)
        alphaP8c = getAlphaFromFT(fft(P8calib),alpha_range_calib)
        
        print "Calibration eyes closed: ", (alphaO1c,alphaP7c,alphaP8c)
        
        #ACTUALLY RUN
        #FIRST FILL RINGBUFFER ONCE AND FFT
        buffinO1 = RingBuffer(N)
        buffinP7 = RingBuffer(N)
        buffinP8 = RingBuffer(N)

        for i in range(N):
            packet = headset.dequeue()
            
            buffinO1.extend(packet.sensors['O1']['value'])
            buffinP7.extend(packet.sensors['P7']['value'])
            buffinP8.extend(packet.sensors['P8']['value'])
            
            gevent.sleep(0)

        ftO1 = fft(buffinO1.get())
        ftP7 = fft(buffinP7.get())
        ftP8 = fft(buffinP8.get())

        timeout = time() + totaltime
        t0 = clock()
        #THEN UPDATE SLIDING DFT AND RINGBUFFER
        countqq = 0
        while time() < timeout:
            countqq = countqq+1
            packet = headset.dequeue()

            #ftO1 = updateFFT(buffinO1.get()[0],packet.sensors['O1']['value'],ftO1,phasediff)
            #ftP7 = updateFFT(buffinP7.get()[0],packet.sensors['P7']['value'],ftP7,phasediff)
            #ftP8 = updateFFT(buffinP8.get()[0],packet.sensors['P8']['value'],ftP8,phasediff)
            
            q1 = packet.sensors['O1']['quality']
            q2 = packet.sensors['P7']['quality']
            q3 = packet.sensors['P8']['quality']
            
            buffinO1.extend(packet.sensors['O1']['value'])
            buffinP7.extend(packet.sensors['P7']['value'])
            buffinP8.extend(packet.sensors['P8']['value'])

            ftO1 = fft(buffinO1.get())
            ftP7 = fft(buffinP7.get())
            ftP8 = fft(buffinP8.get())            
                       
            alphaO1 = getAlphaFromFT(ftO1,alpha_range)   
            
            if countqq<20: print alphaO1      
                       
            alphaO1 = (getAlphaFromFT(ftO1,alpha_range)-alphaO1o)/(alphaO1c-alphaO1o)
            alphaP7 = (getAlphaFromFT(ftP7,alpha_range)-alphaP7o)/(alphaP7c-alphaP7o)
            alphaP8 = (getAlphaFromFT(ftP8,alpha_range)-alphaP8o)/(alphaP8c-alphaP8o)
            
            gevent.sleep(0)
            # THEN USE THESE ALPHAS TOGETHER WITH THE CALIBRATION ONES TO GIVE COMMAND TO DRONE
            # Jin UDP Client
            try:
                alphaScale = (0.5*q1*alphaO1 + 0.25*q2*alphaP7 + 0.25*q3*alphaP8)/(0.5*q1+0.25*q2+0.25*q3+.01)
                #if countqq<20: print alphaScale
                alphaScale = max(0, min(alphaScale,1))    # clamp alpha
                if np.mod(np.trunc(1000*(clock()-t0)),30.0)<3:
                    sock.sendto(str(alphaScale), (host, port))
                    sock.sendto(str(alphaScale), (host, port + 1))

            except socket.error, msg:
                print 'Error Code: ' + str(msg[0]) + ' Message: ' + msg[1]
                
    except KeyboardInterrupt:
        headset.running = False
        headset.close()
        gevent.kill(routine, KeyboardInterrupt)
    finally:
        headset.running = False
        headset.close()
        gevent.kill(routine)
    #sys.exit()
     # Jin UDP Client
    print >>sys.stderr, 'Closing socket'
    sock.close()
    #sys.exit()
