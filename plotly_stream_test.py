'''
    Create a real-time plot using Streaming API from plot.ly
'''

#Import libraries for stream-plot:
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import Stream, Scatter, Data, Layout, Figure

#Math/stats libraries:
import numpy as np

#Module to keep track of date /time:
import time
#import datetime

stream_ids = tls.get_credentials_file()['stream_ids']

#Choose one stream_id from the list:
stream_id = stream_ids[0]

#Create instance of stream ID object:
stream = Stream(token = stream_id, maxpoints = 10)

#Create a trace with embedded stream id object:
trace1 = Scatter(x = [], y = [], mode = 'lines+markers', stream = stream)

data = Data([trace1])

#Layout dictionnary:
layout = Layout(title = 'Test streamig')

#Create Figure object:
fig = Figure(data = data, layout = layout)

#Send fig to plot.ly/ create and open URL/ Initializing streaming plot:
print "Initializing streamning..."
#unique_url = py.plot(fig, filename='first-stream')

#Create instance of Stream LINK object, using same stream_id token:
s = py.Stream(stream_id)

#Open the stream, write in it, then close it:
s.open()

print "Streaming will start in 5 sec..."
time.sleep(1) # wait a few seconds to let the time to swhitch window/tabs
unique_url = py.plot(fig, filename='first-stream')
time.sleep(4)

t0 = time.clock()
i = 0
k = 5
N = 100

while i<N:
    i += 1
    
    # Current time or elapsed time on x-axis:
    #x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') # For current time
    t = time.clock()-t0
    x = "%.3f seconds" %t    # for elapsed time since t0
    # On y-axis a noisy sinus:
    y = np.cos(k*2*np.pi*i/50)+np.random.randn()/3.#careful to not have np.array type!!
    
    #Send data to stream:
    s.write(dict(x = x, y = y))
    
    # (!) Write numbers to stream to append current data on plot,
    #     write lists to overwrite existing data on plot (more in 7.2).
    
    time.sleep(0.08)  # (!) plot a point every 80 ms, for smoother plotting

# (@) Close the stream when done plotting
print "Closing stream link object..."
s.close() 