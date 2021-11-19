from machine import Timer, Pin
import neopixel

timer0 = Timer(0)

n = 12
p = 15

np = neopixel.NeoPixel(Pin(p), n)

def set_color(r, g, b):
    for i in range(n):
        np[i] = (r, g, b)
    np.write()
    
    
def lightOn(r, g , b, waitTime):
    set_color(r, g, b)
    timer0.init(period=waitTime, mode=Timer.ONE_SHOT, callback=lambda t: set_color(0, 0, 0))
   