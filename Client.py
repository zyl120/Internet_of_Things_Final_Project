import argparse
import socket
import re
import json
import sys
from datetime import datetime
import vlc
import rssi
import time


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


def get_host_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]
    finally:
        s.close()
    return ip


def hotspotDistance(SSIDs, SU, MP, N):
    ap_info = rssi_scanner.getAPinfo(networks=SSIDs, sudo=SU)
    try:
        rssi = ap_info[0]["signal"]
    except:
        rssi = -100
    
    distance = 10**((MP-rssi)/(10*N))
    return distance


def hotspotRSSI(SSIDs, SU):
    ap_info = rssi_scanner.getAPinfo(networks=SSIDs, sudo=SU)
    try:
        rssi = ap_info[0]["signal"]
    except:
        rssi = -100
    return rssi


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
                elif(msg[1] == "MEASURESSID"):
                    # Hotspot based distance measurement (currently used)
                    dist = hotspotDistance(ssid, True, -40, 3)
                    dist_str = str(dist)
                    sendMessage(name, "DIST", dist_str)
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
                    try:
                        streamMedia.play()
                    except:
                        streamMedia.stop()
                    finally:
                        streamMedia.play()
                elif(msg[1] == "ENDSTREAM"):
                    streamMedia.stop()
            elif(msg[0] == "RSSI"):
                if(msg[1] == "MEASURERSSI"):
                    rssi = hotspotRSSI(ssid, True)
                    rssi_str = str(rssi)
                    sendMessage(name, "RSSI", rssi_str)
            else:
                continue

    except ConnectionRefusedError:
        print("Connection refused. You need to run server program first.")
    finally:
        s.close()