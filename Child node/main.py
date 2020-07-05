## Code for Nodal Client MCUs

## --------------------------------------------- Import necessary modules -------------------------------------------- ##

from micropython import mem_info
import gc
import utime
import usocket
from network import WLAN
import machine
import bme280
import ustruct

## ------------------------------------------------------------------------------------------------------------------- ##



## --------------------------------------------------- WiFi Settings ------------------------------------------------- ##

start = utime.ticks_ms()

## Set WLAN mode to STA (station/client)
wlan = WLAN(mode = WLAN.STA)
wlan.scan()                                             ## scan for available networks
wlan.connect('repeater_layer', auth = (WLAN.WPA2, 'password123'))

## Goes to deep sleep without active network in 10 seconds
disc_counter = 0
while not wlan.isconnected():
    print("no. of tries: ", disc_counter)
    if disc_counter >= 10:
        print("Total time elapsed (s): ", utime.ticks_diff(start, utime.ticks_ms())/1000)
        print("It's been 10 seconds without a connection. Going to deep sleep...")
        machine.deepsleep(10000)
    utime.sleep(1)
    disc_counter += 1

print(wlan.ifconfig())

## ------------------------------------------------------------------------------------------------------------------- ##



## ------------------------------------ Function to take sensor reading and send data -------------------------------- ##

def read_and_send():
    
    ## Reads sensor data
    i2c = machine.I2C(0)
    bme = bme280.BME280(i2c = i2c)
    temp, press, hum = bme.values       ## Assign measured value to temp, press, hum
    temp = float(temp[:-1])             ## Convert temperature to floating number
    press = float(press[:-3])           ## Convert pressure to floating number
    hum = float(hum[:-1])               ## Convert humidity to floating number
    print("Temperature: %.2f C" % (temp))   ## Print temperatureto console
    print("Pressure: %.2f hPa" % (press))   ## Print pressure to console
    print("Humidity: %.2f %%\n" % (hum))      ## Print humidity to console

    location_code = 369                 ## Arbitrary code value
    ## 'lifff' - long, int, float, float, float
    ## payload format: <location --- type of sensor --- values (temp, pressure, humidity)> 
    data_payload = ustruct.pack('lifff', location_code, bme280.BME280_I2CADDR, temp, press, hum)
    
    UDP_IP = '192.168.0.105'
    UDP_PORT = 5005

    ## Sends sensor data
    ## Set up UDP socket and connect
    sock = usocket.socket(usocket.AF_INET,usocket.SOCK_DGRAM)

    print ("UDP target IP:", UDP_IP)
    print ("UDP target port:", UDP_PORT)
    print ("message:", data_payload)
    try:
        sock.sendto(data_payload, (UDP_IP, UDP_PORT))
    except OSError:
        print("Error sending data. Going to deep sleep now...")
        machine.deepsleep(6000)
    gc.collect()

## ------------------------------------------------------------------------------------------------------------------- ##



## ----------------------------------------------------- Main Body --------------------------------------------------- ##

read_and_send()
print(mem_info()) #6900
#gc.collect()    #3616 # Power consideration increased mem usage to 3728

# Go into deep sleep
print("Total time elapsed (s): ", utime.ticks_diff(start, utime.ticks_ms())/1000)
print("message sent. Going to sleep now for 20 secs.")
machine.deepsleep(366000)

## ------------------------------------------------------------------------------------------------------------------- ##
