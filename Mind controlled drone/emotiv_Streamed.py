# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to a stream on plotly.

print "Importing packages..."

#Emokit:
from emokit.emotiv import Emotiv
import platform
if platform.system() == "Windows":
    import socket  # Needed to prevent gevent crashing on Windows. (surfly / gevent issue #459)
import gevent

#Streaming plot
import time
import sys
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *

print "Package imported! \n Accessing Emotiv headset..."


stream_ids = tls.get_credentials_file()['stream_ids']
stream_id = stream_ids[3]
stream = Stream(token = stream_id, maxpoints = 200)

#Create a trace with embedded stream id object:
trace1 = Scatter(x = [], y = [], mode = 'lines', stream = stream)
data = Data([trace1])

# Define dictionary of axis style options
axis_style = dict(
    showgrid=False,    # remove grid
    showline=False,    # remove axes lines
    zeroline=False     # remove x=0 and y=0 lines
)
#Layout dictionnary:
layout = Layout(
    title='Emotiv Gyro data streamed',  # set plot's title
    xaxis=XAxis(
        axis_style,     # add style options
        range=[-50,50]    # set x-axis range
    ),
    yaxis=YAxis(
        axis_style,     # add style options
        range=[-50,50]  # set y-axis range
    ),
    showlegend=False    # remove legend
)
#Create Figure object:
fig = Figure(data = data, layout = layout)

print "Openning stream of data in URL..."
time.sleep(2)
unique_url = py.plot(fig, filename='Emotiv-Gyro')

#Create instance of Stream LINK object, using same stream_id token:
s = py.Stream(stream_id)  
s.open()
t0 = time.clock()

headset = Emotiv()
routine = gevent.spawn(headset.setup)
gevent.sleep(0)

try:
    while True:
        packet = headset.dequeue()
        #print packet.gyro_x, packet.gyro_y
        #if time.clock()-t0>0.1        
        gevent.sleep(0) # ok to interrupt!
        s.write(dict(x = packet.gyro_x, y= packet.gyro_y))
        #gevent.sleep(0.05)
        #time.sleep(0.04)        
except KeyboardInterrupt:
    headset.running = False
    headset.close()
    gevent.kill(routine)
finally:
    headset.close()
    gevent.kill(routine)
    #s.close()
s.close()
sys.exit()