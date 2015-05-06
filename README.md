# Imperial-festival
files, scripts , etc... used for 9/10 May festival (DRONE/EEG)

## Working examples

All You need is in the Mind-controlled Drone Folder. Be careful if you have an emokit package installed on your python, then any files that does "import emokit" will use your installed package EXCEPT if you run it directly from this folder (Mind Controlled Drone).
For instance, to have the Gyro values printed in the console, run (From this folder in your local path!):
> python example.py

To see the render with the graphs etc... Run
> python render.py

Finally for the alpha rhythms (the most important!), some functions are in the file (getAlphaAndFiltering.py) to show you a way to implement filters etc... Run this:
> python getAlphaAndFiltering.py

### Depedencies
For emokit/alpha waves/plotting... You will need, roughly:
- gevent
- Crypto
- pywinusb (Windows only)
- pygame (for your python version and be careful to get the 32/64 bits version according to your platform)
- scipy and numpy

### TODOS
We need to try:

- Buffering the data + apply usual fft (scipy) to the buffer (Ben/ Jin?)
- Apply a sliding window DFT... (Hugo?)

And we need to sort out:
- Plotting
- Merging Client/Server code

## Random stuff

In the "Testing real-time plot, etc..." Folder you will find a lot of scripts that I used to try out different way to:
- Plot in real -time (using Plotly)
- Handle Key event (using Tkinter  or Qt or Pygame)
- Get alpha waves...

Probably none of them will compile since they all used different kind of libraries that you need first to install.
(Have a look at the plotly stuff it might be cool to use that)
