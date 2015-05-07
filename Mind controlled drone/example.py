# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 

from emokit.emotiv import Emotiv
import platform
if platform.system() == "Windows":
    import socket  # Needed to prevent gevent crashing on Windows. (surfly / gevent issue #459)
import gevent
import sys
import msvcrt

if __name__ == "__main__":
    headset = Emotiv()
    routine = gevent.spawn(headset.setup)
    gevent.sleep(0)
    try:
        while True:
            if msvcrt.kbhit() and msvcrt.getch==chr(27):
                break
            packet = headset.dequeue()
            print packet.gyro_x, packet.gyro_y, packet.battery
            gevent.sleep(0)
    except Exception,ex:
        headset.running = False
        headset.close()
        gevent.kill(routine)
        print ex
    finally:
        headset.running = False
        headset.close()
        gevent.kill(routine)
        print "msg"
    sys.exit()