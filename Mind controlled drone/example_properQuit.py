# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 

from emokit.emotiv import Emotiv
import platform
if platform.system() == "Windows":
    import socket  # Needed to prevent gevent crashing on Windows. (surfly / gevent issue #459)
import gevent
import sys
import pygame

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    headset = Emotiv(display_output=True)
    routine = gevent.spawn(headset.setup)
    gevent.sleep(0)
    while headset.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                headset.running = False
                gevent.kill(routine) #ME!!
                headset.close()          
                break
        packets_in_queue = 0
        try:
            while packets_in_queue < 8 and headset.running:
                packet = headset.dequeue()
                print packet.gyro_x, packet.gyro_y, packet.battery
                #gevent.sleep(0)
                packets_in_queue += 1
        except KeyboardInterrupt:#Exception,ex:
            headset.running = False
            headset.close()
            gevent.kill(routine)
            #print ex
        # finally:
            # headset.close()
            # gevent.kill(routine)
        gevent.sleep(0)
    #sys.exit()
    pygame.quit()