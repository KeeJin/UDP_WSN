## Code for WiFi Network Repeater

## --------------------------------------------- Import necessary modules -------------------------------------------- ##

from micropython import mem_info
import gc
import usocket
from network import WLAN
import machine

## ------------------------------------------------------------------------------------------------------------------- ##



## --------------------------------------------------- WiFi Settings ------------------------------------------------- ##

## Set WLAN mode to STA_AP (station & access point)
print("Setting up wlan access point...")
wlan = WLAN(mode = WLAN.STA_AP, ssid = 'repeater_layer', auth = (WLAN.WPA2, 'password123'), channel=7, antenna=WLAN.INT_ANT)
print("wlan mode set up: with WPA2 authentication\n")

## Set static IP address for server
wlan.ifconfig(id = 1, config=('192.168.0.105', '255.255.255.0', '192.168.0.1', '192.168.0.1'))

## ------------------------------------------------------------------------------------------------------------------- ##



## ------------------------------------------ Function to handle incoming data --------------------------------------- ##

def data_rcv(data):

    ## Connect to server
    wlan.scan()
    wlan.connect('server_layer', auth = (WLAN.WPA2, 'Password123'))
    while not wlan.isconnected():
        machine.idle()
    print(wlan.ifconfig())

    LAYER1_IP = '192.168.0.104'
    LAYER1_PORT = 6006
    
    ## Set up UDP socket and connect
    print("Passing data on to next level...")
    sock_temp = usocket.socket(usocket.AF_INET,usocket.SOCK_DGRAM)
    sock_temp.sendto(data, (LAYER1_IP, LAYER1_PORT))
    
    ## Close socket
    sock_temp.close()

    gc.collect()

## ------------------------------------------------------------------------------------------------------------------- ##



## ----------------------------------------------------- Main Body --------------------------------------------------- ##

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

## Set up UDP socket and bind
sock = usocket.socket(usocket.AF_INET,usocket.SOCK_DGRAM)
sock.settimeout(376)                        ## Set 376 seconds timeout
sock.bind((UDP_IP, UDP_PORT))
print('Socket binded.')

## Main loop
while True:
    try:
        data, addr = sock.recvfrom(40)      ## buffer size is 40 bytes
        print("received message:", data)
        print("source: ", addr)
    except TimeoutError:
        print("TimeoutError(376s). Going to deep sleep.")
        machine.deepsleep(60000)
    data_rcv(data)
    print("Data sent out.")
    gc.collect()

## ------------------------------------------------------------------------------------------------------------------- ##

