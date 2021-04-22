import argparse
import socket
import re
from datetime import datetime
import time
import numpy as np


def sendMessage(connection, name, type, message):
    name = str(name)
    type = str(type)
    message = str(message)
    fname = name.ljust(6, " ")
    ftype = type.ljust(6, " ")
    fmessage = message.ljust(52, " ")
    tdata_exp = fname + ftype + fmessage
    print("[SEND]  " + tdata_exp)
    try:
        connection.send(tdata_exp.encode())
    except:
        print(name, "is offline")
        exit(1)


def sendGlobalMessage(clist, name, type, message):
    for i in range(len(clist)):
        sendMessage(clist[i], name, type, message)


def recvMessage(connection):
    try:
        rdata_bytes = connection.recv(64)
    except:
        print("Device offline is detected")
        exit(1)

    else:
        rdata = rdata_bytes.decode()
        print("[RECV]  " + rdata)
        dname = rdata[0:6].strip(" ")
        dtype = rdata[6:12].strip(" ")
        dmessage = rdata[12:64].strip(" ")
        return (dname, dtype, dmessage)


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int, default=1234,
                    help="port of the server to connect", required=True)
parser.add_argument(
    "-a", "--address", help="address of the music streaming server", default = "http://192.168.0.103:8080",
     required=True)
parser.add_argument("-n", "--number", type=int, default=1, help="number of clients in the network", required=True)
parser.add_argument("-s", "--ssid", default = "Mix2", help="Hotspot SSID", required=True)
args = parser.parse_args()
port = args.port
stream = args.address
num_clients = args.number
ssid = args.ssid
rejected_ip = set()
allowed_ip = set()
name = "ALL"

threads = [None] * num_clients
results = [None] * num_clients
old_results = [-100] * num_clients
error_counts = [0] * num_clients
connections = [None] * num_clients
names = [None] * num_clients

pos_A = np.array((-42.9, -61.3, -72.6))
pos_B = np.array((-64.53, -31.88, -65.02))
pos_C = np.array((-67.97, -58.45, -58.75))

try:
    print("=" * 79)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen(num_clients)
    count = 0
    while True:
        print("waiting for connection")
        c, addr = s.accept()
        if addr[0] in rejected_ip:
            c.close()
            continue
        if addr[0] not in allowed_ip:
            flag = input("allow connection from "+addr[0]+"?")
            if (flag == "y" or flag == "Y"):
                allowed_ip.add(addr[0])
            else:
                rejected_ip.add(addr[0])
                c.close()
                continue
        msg = recvMessage(c)
        names[count] = msg[0]
        connections[count] = c
        
        count += 1

        if(count == num_clients):
            break


    print("all devices found")

    sendGlobalMessage(connections, name, "SADDR", stream)
    sendGlobalMessage(connections, name, "HSADDR", ssid)

    for i in range(len(connections)):
        sendMessage(connections[i], "ALL", "TIME", "REPORTTIME")
        msg = recvMessage(connections[i])

    while True:
        #sendGlobalMessage(connections, "ALL", "CMD", "MEASURESSID")
        sendGlobalMessage(connections, "ALL", "RSSI", "MEASURERSSI")
        dist = [100,100,100]
        # First get distance measurement from client
        for i in range(len(connections)):
            msg = recvMessage(connections[i])
            # Get the RSSI reading from the clients.
            if (msg[0] == names[0]):
                if (msg[2] == "-100"):
                    results[0] == old_results[0]
                else:
                    results[0] = float(msg[2])
                    old_results[0] = results[0]
            elif (msg[0] == names[1]):
                if (msg[2] == "-100"):
                    results[1] == old_results[1]
                else:
                    results[1] = float(msg[2])
                    old_results[1] = results[1]
            else:
                if (msg[2] == "-100"):
                    results[2] == old_results[2]
                else:
                    results[2] = float(msg[2])
                    old_results[2] = results[2]
        
        # Create np array for calculation.
        results = np.array(results)
        print("[INFO]  " + str(results))
        dist[0] = np.linalg.norm(results - pos_A)
        dist[1] = np.linalg.norm(results - pos_B)
        dist[2] = np.linalg.norm(results - pos_C)
        print("[INFO]  " + str(dist))

        # Find the smallest distance in the dist list
        min_value = min(dist)
        min_index = dist.index(min_value)

        sendMessage(connections[min_index], names[min_index], "AUDIO", "STARTSTREAM")
        time.sleep(1.75) # Minimize the delay

        for i in range(len(connections)):
            if(i != min_index):
                sendMessage(connections[i], names[i], "AUDIO", "ENDSTREAM")
        #time.sleep(1.75)
            
    for i in range(len(connections)):
        sendMessage(connections[i], "ALL", "CMD", "STOP")
        connections[i].close()


except ConnectionRefusedError:
    print("Connection refused. You need to run server program first.")
finally:  # must have
    print("free socket")
    s.close()
