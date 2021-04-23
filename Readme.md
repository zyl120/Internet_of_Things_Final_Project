This is the description file for the IoT final project


In the final project, 3 Raspberry Pis, 3 wired speakers, one control computer and one streaming server to build a network to control wired speakers. Raspberry Pi can also be used to be the control computer. For the streaming server, you need a computer with VLC media player installed. The user need to have a phone with mobile hotspot capabilities. 


**Short Demo:** [Short Demo](https://youtu.be/-1pG2TTVRKY)  
**Full Demo:** [Full Demo](https://youtu.be/Ytn-jPnTPTY)  
**Slides:** [Google Slides](https://docs.google.com/presentation/d/1ZKCDQBvoIXoaRCJKD-73gI4yF7cQ5Ve4T34pEpJ1A2Q/edit?usp=sharing)  
**Final Report:** [Google Docs](https://docs.google.com/document/d/1tK4vvEy43rZNPsVUKbmMAsqnzWZ4k2_EBfzdRdwpKUE/edit?usp=sharing)


# Set up streaming server
1. Install VLC media player from the [VLC Official Site](https://www.videolan.org/).
2. With the VLC media player window open, click `Media` button on the top left corner. Then select `Stream...` option.
3. With the `Open Media` window open, click `Add...` button under the `File` tab. Then choose the music file you want to stream. A file with long time duration is recommended as VLC does not support streaming list of music files.
4. After selecting the music file, click `Stream` button on the bottom right corner. Then click `Next` button again until you see the `Destination Setup` window.
5. In the `Destination Setup` window, select `HTTP` as the `New destination`. Then click `Add` button. If you want listen to the stream on the server as well, check the `Display locally` box. Under the `HTTP` tab, set the `Port` number. Do not change the `Path`. Then click `Next` button.
6. In the `Transcoding Options` window, check `Activate Transcoding` box. Select `Audio - MP3` or `Audio - FLAC` as the profile depending on the original music file format. Then click `Next` button.
7. In the `Option Setup` window, do not change anything, click `Stream` button on the bottom right corner.
8. Then streaming server is now set up.  
------------------
or alternatively, use some online radio stations, such as [WRPI](https://www.wrpi.org/).

# Find the location fingerprint of the speakers
1. Download the `RSSI_Server.py` file.
2. `python3 RSSI_Server.py -p [port number] -a [address of streaming server, e.g. http://192.168.0.100:8080] -n [number of Raspberry Pis in the network] -s [SSID of the mobile hotspot]`. If there is no dependency error, you should see `waiting for connection` shown in the terminal. 
3. Then we need to setup the 3 Raspberry Pis as clients. 
4. After setting up the clients, the program will automatically run the RSSI scan of the provided mobile hotspot SSID 100 times. Then the program will print the average RSSI from the three Raspberry Pis. Use the readings to build a fingerprint based localization database. 
5. Modify the `Server.py` file to reflect the RSSI readings. (E.g., `RSSI.xlsx` and  
pos_A = np.array((-42.9, -61.3, -72.6))  
pos_B = np.array((-64.53, -31.88, -65.02))  
pos_C = np.array((-67.97, -58.45, -58.75))  
)

# Set up control server
1. Download the `Server.py` file.
2. Run the script with `python3 Server.py -p [port number] -a [address of streaming server, e.g. http://192.168.0.100:8080] -n [number of Raspberry Pis in the network] -s [SSID of the mobile hotspot]`. If there is no dependency error, you should see `waiting for connection` shown in the terminal. 
3. Then we need to setup the 3 Raspberry Pis as clients.

# Set up clients
1. Before running the Python script, you need to run `pip3 install python-vlc` and `pip3 install rssi` to install the 2 dependencies.
2. You should follow [github page](https://github.com/jvillagomez/rssi_module/issues/1) to modify one error in the `rssi` module.
3. Download the `RSSI_Raspberry.py` file to the Raspberry Pis.
4. Run the script with `python3 RSSI_Raspberry.py -s [server address] -p [port number] -n [name for this client]`. 
5. Ideally, when the control server and Raspberry Pi are under the same network, you should see `allow connection from IP_ADDRESS?` message on the control server terminal. You should check the prompted ip address with the actual Raspberry Pi address. To allow connection, type `y` in the control server terminal.
6. Repeat the above procedures to connect all clients to the control server.
7. After all clients are setup, the control server will send command to the clients to control the audio playback. You should hear the music from streaming server with the headphone connected to the clients. Only one device will play the music at the same time.


# Command Details
Each TCP message consists of 64 characters. The server and clients will create a buffer of size 64 each time to avoid data loss. The structure is as follows:  
|name(6 characters)|type(6 characters)|message(52 characters)|  
The name is 6 characters long. The type is 6 characters long. The message is 52 characters long. If the server wants to send a global message the name `ALL` is used as the indicator.
Below is the table for all possible types and messages:
|Type|Message|Description|
|----|-------|-----|
|SADDR| the streaming server address| server &#8594; clients, the clients will set the streaming server address.|
|HSADDR| the name of mobile hotspot| server &#8594; clients, the clients will set the hotspot name for RSSI localization.|
|TIME| REPORTTIME| server &#8594; clients, the clients will send the client local time back to the server.|
|CMD|STOP| server &#8594; clients, the clients will disconnect from the server.|
|AUDIO|STARTSTREAM| server &#8594; clients, the clients will start to play the audio.|
|AUDIO|ENDSTREAM| server &#8594; clients, the clients will stop the audio.|
|RSSI| MEASURERSSI| server &#8594; clients, the clients will send the RSSI of the mobile hotspot to the server.|
|RSSI| RSSI reading of the hotspot| server &#8592; clients, the clients will send the RSSI of the mobile hotspot to the server.|
|DIST| the measured distance| server &#8592; clients, the clients will send the distance based on RSSI localization to the server.|
|IP| the local IP address| server &#8592; clients, the clients will send the localhost IP to the server.|  

All other spaces in the message will be filled with `␣`.

