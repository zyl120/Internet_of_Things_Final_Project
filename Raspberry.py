import argparse
import socket
import re
import json
import sys
from datetime import datetime
import vlc
import random
import RPi.GPIO as GPIO
from HCSR04_lib import HCSR04
import rssi
import threading
import time
import multiprocessing


def RSAKeygen():
    gap = random.randint(2**27, 2**29)
    p = npkg.find_prime_smaller_than_k(2**31-gap)
    q = npkg.find_prime_greater_than_k(2**31-gap)
    e = 65537
    N = p * q
    d = npkg.mult_inv_mod_N(e, (p-1)*(q-1))
    return e, d, N


def RSA_decrypt(c, d, N):
    m = npkg.exp_mod(c, d, N)
    return m


def bytearray_xor(key, msg_bytes):
    # this is not a good encryption method, but it's a way :)

    # key to bytes
    key_bytearray = key.to_bytes(math.ceil(math.log2(key)), byteorder="big")

    key_len, msg_len = len(key_bytearray), len(msg_bytes)

    return bytearray(msg_bytes[i] ^ key_bytearray[i % key_len] for i in range(msg_len))


def sendMessage(name, type, message):
    name = str(name)
    type = str(type)
    message = str(message)
    fname = name.ljust(6, " ")
    ftype = type.ljust(6, " ")
    fmessage = message.ljust(52, " ")
    tdata_exp = fname + ftype + fmessage
    print("[SEND]  " + tdata_exp)
    s.send(tdata_exp.encode())


def recvMessage():
    try:
        rdata_bytes = s.recv(64)
    except:
        print("Server is down")
        exit(1)
    finally:
        rdata = rdata_bytes.decode()
        print("[RECV]  " + rdata)
        dname = rdata[0:6].strip(" ")
        dtype = rdata[6:12].strip(" ")
        dmessage = rdata[12:64].strip(" ")
        if (dname == "ALL" or dname == name):
            return (dtype, dmessage)
        else:
            print("Data compromised")
            exit(1)
            #return ("NULL", "NULL")


def measureDistance():
    distance = int(instance.measure_distance())
    return distance


def get_host_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]
    finally:
        s.close()
    return ip


def bluetoothDistance():
    print("Measuring BT")
    result=bluetooth.lookup_name("20:47:da:aa:d9:e7",timeout=1)
    if(result !=None):
        print("user near")
    else:
        print("user far")


def hotspotDistance(SSIDs, SU, MP, N):
    ap_info = rssi_scanner.getAPinfo(networks=SSIDs, sudo=SU)
    try:
        rssi = ap_info[0]["signal"]
    except:
        rssi = -100
    
    distance = 10**((MP-rssi)/(10*N))
    return distance


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", type=str, default="127.0.0.1",
                        help="A string of server IP (default: 127.0.0.1)")
    parser.add_argument("-p", "--port", type=int,
                        help="port of the server to connect", required=True)
    parser.add_argument("-n", "--name", help="name of device", required=True)
    args = parser.parse_args()

    # get the ip and port of the server
    ip = args.server
    port = args.port
    name = args.name
    streamServer = ""
    streamMedia = vlc.MediaPlayer()

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()

    TRIG = 4
    ECHO = 17

    GPIO.setup(TRIG, GPIO.OUT)

    instance = HCSR04(TRIG_pin=TRIG, ECHO_pin=ECHO)  # BCM17
    instance.init_HCSR04()

    interface = "wlan0"
    rssi_scanner = rssi.RSSI_Scan(interface)
    ssid = list()

    print("Trying to connect to %s:%d" % (ip, port))

    msg = b""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        myip = get_host_ip()

        sendMessage(name, "IP", myip)
  
        while True:
            msg = recvMessage()
            if(msg[0] == "CMD"):
                if(msg[1] == "STOP"):
                    s.close()
                    break
                elif(msg[1] == "MEASUREDIST"):
                    dist = measureDistance()
                    dist_string = str(dist)
                    sendMessage(name, "DIST", dist_string)
                elif(msg[1] == "MEASUREBLUETOOTH"):
                    bluetoothDistance()
                elif(msg[1] == "MEASURESSID"):
                    dist = hotspotDistance(ssid, True, -40, 2)
                    dist_str = str(dist)
                    sendMessage(name, "DIST", dist_str)
                    #ap_info = rssi_scanner.getAPinfo(networks=ssid, sudo=True)
                    #print(ap_info[0]["signal"])
                    #print(ap_info)
            elif(msg[0] == "TIME"):
                if(msg[1] == "REPORTTIME"):
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    sendMessage(name, "TIME", current_time)
            elif(msg[0] == "SADDR"):
                streamServer = msg[1]
                streamMedia = vlc.MediaPlayer(streamServer)
            elif(msg[0] == "HSADDR"):
                ssid.append(msg[1])
            elif(msg[0] == "AUDIO"):
                if(msg[1] == "STARTSTREAM"):
                    #streamMedia.stop()
                    try:
                        streamMedia.play()
                    except:
                        streamMedia.stop()
                    finally:
                        streamMedia.play()
                elif(msg[1] == "ENDSTREAM"):
                    streamMedia.stop()
            else:
                continue

    except ConnectionRefusedError:
        print("Connection refused. You need to run server program first.")
    finally:
        s.close()