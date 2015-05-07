# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 

from emokit.emotiv import Emotiv
import platform
if platform.system() == "Windows":
    import socket  # Needed to prevent gevent crashing on Windows. (surfly / gevent issue #459)
import gevent
import sys
import csv

import numpy as np
from scipy.signal import butter, lfilter

csv_writer = csv.writer(open("rawdataHugo_closed.csv","wb"), delimiter=',')

sensornames = ['F3','FC5','AF3','F7','T7','P7','O1','O2','P8','T8','F8','AF4','FC6','F4']
csv_writer.writerow(sensornames)

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
    headset = Emotiv()
    routine = gevent.spawn(headset.setup)
    gevent.sleep(0)
    try:
        for i in range(2048):
            buffin = []
            #for i in xrange(128):
            packet = headset.dequeue()                
            aa=[]
            for sensorname in sensornames:
                aa.append(packet.sensors[sensorname]['value'])
                #print aa                              
            csv_writer.writerow(aa) 
                #csv_writer.writerow('\n')

                #buffin.append(packet.sensors['F3']['value'])
                #print packet.gyro_x, packet.gyro_y, packet.battery
            gevent.sleep(0)
            if i==2047: 
                print "Finished! Kill me..."
                break
            #alpha = getAlphaPower(buffin)
            #print alpha
    except KeyboardInterrupt:
        headset.running = False
        headset.close()
        gevent.kill(routine, KeyboardInterrupt)
    finally:
        headset.running = False
        headset.close()
        gevent.kill(routine)
    #sys.exit()
