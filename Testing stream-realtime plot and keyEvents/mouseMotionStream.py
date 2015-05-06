from Tkinter import *

def motion(event):
  print("Mouse position: (%s %s)" % (event.x, event.y))
  return

#Tkinter window:
master = Tk()

whatever_you_do = """Whatever you do will be insignificant, but it is very important that you do 
it.\n(Mahatma Gandhi)"""

#Message box
msg = Message(master, text = whatever_you_do)
msg.config(bg='lightgreen', font=('times', 24, 'italic'))

#Binding callbacks + packing:
msg.bind('<Motion>',motion)
msg.pack()

#Mainloop (waiting for event):
master.mainloop()