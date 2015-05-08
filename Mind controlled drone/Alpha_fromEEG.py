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
    if ffttype=='log': Power = 10.*np.log10(Power)     # Log/Linear
    spectrum = zip(freq,Power)      #This is a list of "tuples" (freq, value)...
    alphalist = []                  # Taking the power of alpha rhythms into this list
    for (f,S) in spectrum:
        if f>=8 and f<=12:          #You cannot do more basic filtering...
            alphalist.append(S)
    #alpha = np.amax(alphalist)      #mean is bad, max is not relativ ptp is probably the best, var depends on number of points...
    alpha = np.ptp(alphalist)
    #alpha = np.var(alphalist)
    return alpha
    
#def calibration(N_calib=2048, Nsample=256, Fs = 128.):
    
    

if __name__ == "__main__":
    import csv
    
    N = 256
    #inp = raw_input("Choose the size of the buffer processed by FFT: \n")
    #N = int(inp)
    Ncalib = 2048
    #inp = raw_input("Choose the size of the calibration vectors: \n")
    #Ncalib = int(inp)
    #ffttype = 'log'
    ffttype = raw_input("What kind of scale? 'log'-'square'-or 'abs'?\n")
    param = dict.fromkeys(['log','abs','square'],[[0.,0.],[-1.,-1.],[1.,1.]])
    default_param = dict({'square':[10.,100.] , 'log':[6.,30.], 'abs':[5.,20.]})  # [min value (eyes open), max (eyes closed)]
    if param.keys().count(ffttype) == 0:
        ffttype = 'square'
        print "Scale not valid. Square chosen by default..."
        
    buffin = RingBuffer(N)
    
    headset = Emotiv()
    routine = gevent.spawn(headset.setup)
    gevent.sleep(0)
    
    win = scipy.hamming(N)
    normalizing = np.sum(np.multiply(win,np.ones(N)*1./N))
    #win = np.ones(N)
    
    ######### CALIBRATION##########################
    Name = raw_input("Type your name:\n")
    filename = ["./Data_festival/rawdata_"+Name+"_open.csv","./Data_festival/rawdata_"+Name+"_closed.csv"]
    instructions = ["PLEASE KEEP STILL EYES WIDE OPEN\n Press Enter when you are ready...","PLEASE KEEP YOUR EYES CLOSED AND STAY STILL, AS RELAXED AS YOU CAN...\n Press Enter when you are ready..."]
    #Recording data:
    for k in range(2):
        #headset.running = False
        print instructions[k]
        raw_input()
        f = open(filename[k],"wb")
        csv_writer = csv.writer(f, delimiter=',')
        sensornames = ['F3','FC5','AF3','F7','T7','P7','O1','O2','P8','T8','F8','AF4','FC6','F4']
        csv_writer.writerow(sensornames)
        # headset.dequeue()
        # gevent.sleep(0)
        #headset.running = True
        for i in range(Ncalib):
            packet = headset.dequeue()
            #gevent.sleep(0)                
            aa=[]
            for sensorname in sensornames:
                aa.append(packet.sensors[sensorname]['value'])
                #print aa                              
            csv_writer.writerow(aa) 
            gevent.sleep(0)
            if i==Ncalib-1: 
                print "Finished! Kill me..."
                break
        f.close()
        print f
    #Reading files:
    with open(filename[0], 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        data_open = []
        for row in spamreader:
            data_open.append(row)
    with open(filename[1], 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        data_closed = []
        for row in spamreader:
            data_closed.append(row)
    #Formatting data:
    data_open.remove(sensornames)
    data_closed.remove(sensornames)
    data_open = np.array(data_open, dtype = '|S4').astype(np.float).transpose()
    data_closed = np.array(data_closed, dtype = '|S4').astype(np.float).transpose()
    #Calculating calibration parameters from Fourier trasnform:
    for key in param.keys():
        param[key][0] = getAlphaPower(data_open[6][:],key)  #Recording O1 sensor only.... :(
        param[key][1] = getAlphaPower(data_closed[6][:],key)
    #print "Calibration ends... (Value kept: [%f,%f])" %tuple(param[ffttype])
    #param = default_param
    ######## END OF CALIBRATION#######################
    
    print "... Start main loop:"
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
            temp_buffer.append(packet.sensors['O1']['value']) 
            gevent.sleep(0)
        buffin.extend(temp_buffer)
        #print getAlphaPower(np.multiply(win,buffin.get())) # hamming window to sharpen fft
        while True:            
            packet = headset.dequeue()
            buffin.extend(packet.sensors['O1']['value'])
            gevent.sleep(0)
            alpha = getAlphaPower(np.multiply(win,buffin.get())/normalizing,ffttype)  # hamming window to sharpen fft
            #print alpha
            
            # Jin UDP Client
            try:
                alphaScale = (alpha - 1.2*param[ffttype][0])/(1.2*param[ffttype][1]-1.2*param[ffttype][0])
                #alphaScale = alphaScale*int(packet.sensors['O1']['quality']>1) #/7 # or /4...
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