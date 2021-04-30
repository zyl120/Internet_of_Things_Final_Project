import argparse
import socket
import re
from datetime import datetime
import time


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
connections = [None] * num_clients
names = [None] * num_clients
RSSI0 = list()
RSSI1 = list()
RSSI2 = list()


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

    for _ in range(100):
        sendGlobalMessage(connections, "ALL", "RSSI", "MEASURERSSI")
        for i in range(len(connections)):
            msg = recvMessage(connections[i])
            if (msg[2] != "-100"):
                if i == 0:
                    RSSI0.append(float(msg[2]))
                elif i == 1:
                    RSSI1.append(float(msg[2]))
                else:
                    RSSI2.append(float(msg[2]))
        time.sleep(0.5)

    rssi_avg0 = 0
    rssi_avg1 = 0
    rssi_avg2 = 0
    if (len(connections) == 1):
        rssi_avg0 = sum(RSSI0) / len(RSSI0)
    elif (len(connections) == 2):
        rssi_avg0 = sum(RSSI0) / len(RSSI0)
        rssi_avg1 = sum(RSSI1) / len(RSSI1)
    else:
        rssi_avg0 = sum(RSSI0) / len(RSSI0)
        rssi_avg1 = sum(RSSI1) / len(RSSI1)
        rssi_avg2 = sum(RSSI2) / len(RSSI2)

    print(rssi_avg0, rssi_avg1, rssi_avg2)

    for i in range(len(connections)):
        sendMessage(connections[i], "ALL", "CMD", "STOP")
        connections[i].close()


except ConnectionRefusedError:
    print("Connection refused. You need to run server program first.")
finally:  # must have
    print("free socket")
    s.close()
