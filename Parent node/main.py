## Code for Network Gateway MCU

## --------------------------------------------- Import necessary modules -------------------------------------------- ##

from micropython import mem_info
import gc
import usocket
from network import WLAN
import ustruct
from mqtt import MQTTClient
import machine
import utime

## ------------------------------------------------------------------------------------------------------------------- ##



## ---------------------------------------------- Dictionary definitions --------------------------------------------- ##

sensor_dict = {
    0x77 : "bme280"
    # Add more sensors here #
    }

loc_dict = {
    369 : "TR369"
    12 : "TR12"
    21 : "Level_2_Conference_Room"
    # Add more rooms here #
    }

## ------------------------------------------------------------------------------------------------------------------- ##



## --------------------------------------------------- WiFi Settings ------------------------------------------------- ##

## Set WLAN mode to STA_AP (station & access point)
print("Setting up wlan access point...")
wlan = WLAN(mode = WLAN.STA_AP, ssid = 'server_layer', auth = (WLAN.WPA2, 'Password123'), channel=7, antenna=WLAN.INT_ANT)
print("wlan mode set up: with WPA2 authentication.\n")

## Connect to internet
wlan.connect("RCBB-2", auth=(WLAN.WPA2, "bkind2all"), timeout=5000)
##wlan.connect("SKY", auth=(WLAN.WPA2, "dmw540935"), timeout=5000)

while not wlan.isconnected():
    machine.idle()
print("Connected to WiFi\n")

## Set static IP address for server
wlan.ifconfig(id = 1, config=('192.168.0.104', '255.255.255.0', '192.168.0.1', '192.168.0.1'))

## ------------------------------------------------------------------------------------------------------------------- ##



## -------------------------------- Function to unpack byte data and send to MQTT server ----------------------------- ##

def send_data(data_raw):
    
    print("Unpacking raw data...")
    data = ustruct.unpack('lifff', data_raw)
    loc, sensor_type, temp, press, hum = data
    print("Location of measured reading: ", loc)
    print("Sensor type: ", sensor_dict[sensor_type])
    print("Temperature: %.2f C" % (temp))  ## Print temperature to console
    print("Pressure: %.2f hPa" % (press))  ## Print pressure to console
    print("Humidity: %.2f %%" % (hum))   ## Print humidity to console
    print("\n")
    
    print("Sending data up to MQTT server...")
    client = MQTTClient("7a9e85d9-c8ed-40fd-becb-20de9fec2fe3", "io.adafruit.com",user="yoplocheo", password="c75b9079687547a48acc37c9e05c51bf", port=1883)
    client.connect()
    print("Sending temperature...\n")
    client.publish(topic="yoplocheo/feeds/{}_{}_temperature".format(loc_dict[loc], sensor_dict[sensor_type]), msg=str(temp), retain = True)
    utime.sleep_ms(1000)
    print("Sending pressure...\n")
    client.publish(topic="yoplocheo/feeds/{}_{}_pressure".format(loc_dict[loc], sensor_dict[sensor_type]), msg=str(press), retain = True)
    utime.sleep_ms(1000)
    print("Sending hum...\n")
    client.publish(topic="yoplocheo/feeds/{}_{}_humidity".format(loc_dict[loc], sensor_dict[sensor_type]), msg=str(hum), retain = True)
    utime.sleep_ms(1000)
    print("Data sent.\n")

    gc.collect()

## ------------------------------------------------------------------------------------------------------------------- ##



## ----------------------------------------------------- Main Body --------------------------------------------------- ##

UDP_IP = "0.0.0.0"
UDP_PORT = 6006

## Set up UDP socket and bind
sock = usocket.socket(usocket.AF_INET,usocket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print('Socket binded.')
print(mem_info())

while True():
    data_raw, addr = sock.recvfrom(40)      ## buffer size is 40 bytes
    print("raw data payload:", data_raw)
    print("source: ", addr)
    send_data(data_raw)
    print(mem_info()) # 96
    gc.collect()

## ------------------------------------------------------------------------------------------------------------------- ##

