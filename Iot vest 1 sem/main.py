
# Importere library til at forbinde til adafruit.io
from imu import MPU6050
from machine import Pin, PWM
from machine import SoftI2C
from time import sleep_ms
from time import sleep
from time import ticks_ms
from machine import UART
import umqtt_robust2
import GPSfunk
import neopixel
import math
import random
import machine
import time
import delay_1

# uart1 = UART(1, baudrate=9600, tx=33, rx=32)
# STARTBYTE, VER, Len, CMD, FEEDBACK, PARA1, PARA2, PARA3, PARA4, CHECKSUM, ENDBYTE
# play = bytes([0x7E, 0xFF, 0x06, 0x0D, 0x00, 0x00, 0x01, 0xFE, 0xED, 0xEF])
# pause = bytes([0x7E, 0xFF, 0x06, 0x0E, 0x00, 0x00, 0x00, 0xFE, 0xED, 0xEF])
# 
# track1 = bytes ([0x7E, 0xFF, 0X06, 0x12, 0x00, 0x00, 0x01, 0xFE, 0xE8, 0XEF])
# track2 = bytes ([0x7E, 0xFF, 0X06, 0x12, 0x00, 0x00, 0x02, 0xFE, 0xE7, 0XEF])

#0x10
# i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
button = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
imu = MPU6050(SoftI2C(scl=Pin(22), sda=Pin(21)))
hv = ["hojre", "venstre"]
GPS = machine.Pin(16, machine.Pin.OUT)
previousTime = 0
interval = 100000
GPS_state = 0

imu = MPU6050(SoftI2C(scl=Pin(22), sda=Pin(21)))
lib = umqtt_robust2
x = imu.accel.x
y = imu.accel.y
z = imu.accel.z
temp = imu.temperature
accel = math.sqrt(x**2 + y**2 + z **2)

n = 12
p = 15

np = neopixel.NeoPixel(Pin(p), n)

# opret en ny feed kaldet map_gps indo på io.adafruit
mapFeed = bytes('{:s}/feeds/{:s}'.format(b'Nico403y', b'mapfeed/csv'), 'utf-8')
# opret en ny feed kaldet speed_gps indo på io.adafruit
speedFeed = bytes('{:s}/feeds/{:s}'.format(b'Nico403y', b'speedfeed/csv'), 'utf-8')
# opret accel
accelFeed = bytes('{:s}/feeds/{:s}'.format(b'Nico403y', b'accelfeed/csv'), 'utf-8')
# opret temp
tempFeed = bytes('{:s}/feeds/{:s}'.format(b'Nico403y', b'tempfeed/csv'), 'utf-8')



# Commented out while testing to test faster
for i in range(4 * n):
    for j in range(n):
        np[j] = (0, 255, 0)
    if (i // n) % 2 == 0:
        np[i % n] = (255, 0, 0)       
    else:
        np[n - 1 - (i % n)] = (255, 0, 0)
    np.write()
    sleep_ms(60)
    
delay_1.lightOn(175, 175, 175, 2000)
button_push = False
starter = 1

while True:
    currentTime = ticks_ms()
    print(currentTime - previousTime)
    sleep_ms(1500)    
    
    # haandtere fejl i forbindelsen og hvor ofte den skal forbinde igen
    if lib.c.is_conn_issue():
        print("Trying to connect")
        while lib.c.is_conn_issue():
            # hvis der forbindes returnere is_conn_issue metoden ingen fejlmeddelse
            print("Reconnect")
            lib.c.reconnect()
        else:
            print("resubscribe")
            lib.c.resubscribe()
        
    if (currentTime - previousTime > interval):
        previousTime = currentTime
        lib.c.publish(topic=mapFeed, msg=GPSfunk.main())
        speed = GPSfunk.main()
        speed = speed[:4]
        print("speed: ", speed)
        lib.c.publish(topic=speedFeed, msg=speed) 

    while not button_push:
            first = button.value()
            time.sleep(0.01)
            second = button.value()
            if first and not second:
                button_push = True
                starter = 1
                print('Button pressed!')
            elif not first and second:
                print('Button released!')
            while button_push and starter == 1:
                delay_1.lightOn(0, 0, 255, 2000)
                button_push = False
                x = imu.accel.x
                y = imu.accel.y
                z = imu.accel.z
                temp = imu.temperature
                accel = math.sqrt(x**2 + y**2 + z **2)
                # Bliver målt i g   
                retning = random.choice(hv)
                print(retning)
                if retning == "hojre":
                    sleep(2.3)
                    beeper = PWM(Pin(14), freq=455, duty=520)
                    time.sleep(0.7)
                    beeper.deinit()
                    #uart1.write(track1)
                    sleep(0.8)
                    print("hojre")
                    x = imu.accel.x
                    y = imu.accel.y
                    z = imu.accel.z
                    temp = imu.temperature
                    accel = math.sqrt(x**2 + y**2 + z **2)
                    #sleep(0.5)
                    if accel <= 1.7:
                        delay_1.lightOn(255, 0, 0, 2000)
                        print("accel", accel)
                        print("temperature: %3.1f C" % temp)
                        starter = 0
                        button_push = False
                        #break
                    elif accel >= 2.2:
                        delay_1.lightOn(238, 215, 0, 2000)
                        print("accel", accel)
                        print("temperature: %3.1f C" % temp)
                        starter = 0
                        button_push = False
                        #break
                    elif accel >= 2.6:
                        delay_1.lightOn(0, 255, 50, 2000)
                        print("accel", accel)
                        print("temperature: %3.1f C" % temp)
                        starter = 0
                        button_push = False
                        #break
                
                    lib.c.publish(topic=accelFeed, msg=str(accel))
                    temp = imu.temperature
                    accel = math.sqrt(x**2 + y**2 + z **2)
                    lib.c.publish(topic=tempFeed, msg="temperaturen er "+str(temp)+" C")
                    break
                        
                else:
                    print("venstre")
                    sleep(2.3)
                    beeper = PWM(Pin(14), freq=455, duty=520)
                    time.sleep(0.7)
                    beeper.deinit()
                    #uart1.write(track2)
                    sleep(0.2)
                    x = imu.accel.x
                    y = imu.accel.y
                    z = imu.accel.z
                    temp = imu.temperature
                    accel = math.sqrt(x**2 + y**2 + z **2)
                    #sleep(0.5)
                    if accel <= 1.7:
                        delay_1.lightOn(255, 0, 0, 2000)
                        print("accel", accel)
                        print("temperature: %3.1f C" % temp)
                        starter = 0
                        button_push = False
                        #break
                    elif accel >= 2.2:
                        delay_1.lightOn(238, 215, 0, 2000)
                        print("accel", accel)
                        print("temperature: %3.1f C" % temp)
                        starter = 0
                        button_push = False
                        #break
                    elif accel >= 2.6:
                        delay_1.lightOn(0, 255, 50, 2000)
                        print("accel", accel)
                        print("temperature: %3.1f C" % temp)
                        starter = 0
                        button_push = False
                        #break
                
                    lib.c.publish(topic=accelFeed, msg=str(accel))
                    temp = imu.temperature
                    accel = math.sqrt(x**2 + y**2 + z **2)
                    lib.c.publish(topic=tempFeed, msg="temperaturen er "+str(temp)+" C")
                    break
                        
                    

    # Stopper programmet når der trykkes Ctrl + c
#             except KeyboardInterrupt:
#                 print('Ctrl-C pressed...exiting')
#                 lib.client.disconnect()
#                 lib.sys.exit() 
        
#             lib.c.check_msg() # needed when publish(qos=1), ping(), subscribe()
#             lib.c.send_queue()  # needed when using the caching capabilities for unsent messages
#             lib.c.disconnect()
