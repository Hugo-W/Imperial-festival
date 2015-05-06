#!/usr/bin/python3
# write tkinter as Tkinter to be Python 2.x compatible
import Tkinter


class App():
   def __init__(self):
       self.root = Tkinter.Tk()
       button = Tkinter.Button(self.root, text = 'root quit', command=self.quit_root)
       button.pack()
       widget = Tkinter.Button(self.root, text='Mouse Clicks')
       widget.pack()
       widget.bind('<Button-1>', self.hello)
       widget.bind('<Double-1>', self.quit) 
       self.root.mainloop()
       
   def hello(self,event):
       print("Single Click, Button-l") 

   def quit_root(self):
       self.root.destroy()
       import sys; sys.exit()
       
   def quit(self,event):
       self.root.destroy()
       print "Double Click, so let's stop"
       import sys; sys.exit()

if __name__ == "__main__":
    app = App()


#def quit(event):