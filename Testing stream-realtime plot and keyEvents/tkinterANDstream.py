from Tkinter import *
import time
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import Stream, Scatter, Data, Layout, Figure

#Math/stats libraries:
import numpy as np


class MyLoop():
    def __init__(self, root, stream):
        self.running = True
        self.aboutToQuit = False
        self.root = root
        self.someVar = 0
        self.t0 = time.clock()
        self.root.bind("<space>", self.switch)
        self.root.bind("<Escape>", self.exit) 

        while not self.aboutToQuit:
            self.root.update() # always process new events

            if self.running:
                x = time.clock()-self.t0
                # do stuff
                self.someVar = np.cos(x*2*np.pi)
                y = self.someVar
                stream.write(dict(x = x, y = y))
                time.sleep(0.08)  # (!) plot a point every 80 ms, for smoother plotting

            else: # If paused, don't do anything
                time.sleep(.1)

    def switch(self, event):
        print(['Unpausing','Pausing'][self.running])
        self.running = not(self.running)

    def exit(self, event):
        self.aboutToQuit = True
        self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    #root.withdraw() # don't show the tkinter window (causes Canopy to not be able to catch callback functions !!!)
    
    stream_ids = tls.get_credentials_file()['stream_ids']
    stream_id = stream_ids[1]
    stream = Stream(token = stream_id, maxpoints = 50)
    
    #Create a trace with embedded stream id object:
    trace1 = Scatter(x = [], y = [], mode = 'lines+markers', stream = stream)
    data = Data([trace1])
    
    #Layout dictionnary:
    layout = Layout(title = 'Test streamig+ Tkinter')
    #Create Figure object:
    fig = Figure(data = data, layout = layout)
    
    unique_url = py.plot(fig, filename='Streaming + pausing from tkinter')
    
    #Create instance of Stream LINK object, using same stream_id token:
    s = py.Stream(stream_id)
    s.open()
    
    #Launching the class with stream LINK as arg
    MyLoop(root,s)
    root.mainloop()
    
    time.sleep(5) # wait a few seconds to let the time to swhitch window/tabs
    
    # (@) Close the stream when done plotting
    print "Closing stream link object..."
    s.close() 