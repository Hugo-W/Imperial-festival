from Tkinter import *
import tkMessageBox
#import time
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *


class MainLoop:
    def __init__(self, master,streamID, txt):
        self.root = master
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        #Message box
        msg = Message(self.root, text = txt)
        msg.config(bg='lightgreen', font=('times', 24, 'italic'))
        msg.pack()
        #Binding callbacks + packing:
        msg.bind('<Motion>',self.motion)
        #Create instance of Stream LINK object, using same stream_id token:
        self.s = py.Stream(stream_id)
        self.s.open()
        
    def motion(self,event):
        #print("Mouse position: (%s %s)" % (event.x, event.y))
        self.s.write(dict(x = event.x, y = 223-event.y))
        return
        
    def on_closing(self):
        if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.s.close()


if __name__ == "__main__":
    #Tkinter window:
    master = Tk()
    txt = """Whatever you do will be insignificant, but it is very important that you do 
    it.\n(Mahatma Gandhi)"""
    
    stream_ids = tls.get_credentials_file()['stream_ids']
    stream_id = stream_ids[2]
    stream = Stream(token = stream_id, maxpoints = 80)
    
    #Create a trace with embedded stream id object:
    trace1 = Scatter(
        x=[],  # init. data lists
        y=[],    
        mode='lines',                             # path drawn as line
        line=Line(color='rgba(255,76,76,0.45)'), # light blue line color
        stream= stream
    )
        
    # Make data object made up of the 2 scatter objs
    data = Data([trace1]) 
    
    # Define dictionary of axis style options
    axis_style = dict(
        showgrid=False,    # remove grid
        showline=False,    # remove axes lines
        zeroline=False     # remove x=0 and y=0 lines
    )
    # Make layout with title and set axis ranges
    layout = Layout(
        title='Following mouse pointer from Tkinter Win',  # set plot's title
        xaxis=XAxis(
            axis_style,     # add style options
            range=[0,318]    # set x-axis range
        ),
        yaxis=YAxis(
            axis_style,     # add style options
            range=[0,223]  # set y-axis range
        ),
        showlegend=False    # remove legend
    )
    #Create Figure object:
    fig = Figure(data = data, layout = layout)
    
    unique_url = py.plot(fig, filename='Streaming-mouse-motion')

    
    #Launching the class with stream LINK as arg
    MainLoop(master,stream_id,txt)
    master.mainloop()