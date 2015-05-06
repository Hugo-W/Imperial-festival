from Tkinter import *
import time

class MyLoop():
    def __init__(self, root):
        self.running = True
        self.aboutToQuit = False
        self.root = root
        self.someVar = 0
        self.root.bind("<space>", self.switch)
        self.root.bind("<Escape>", self.exit) 

        while not self.aboutToQuit:
            self.root.update() # always process new events

            if self.running:
                # do stuff
                self.someVar += 1
                print(self.someVar)
                time.sleep(.1)

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
    MyLoop(root)
    root.mainloop()