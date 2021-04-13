This is the description file for the IoT final project


In the final project, 3 Raspberry Pis, 3 wired speakers, one control computer and one streaming server to build a network to control wired speakers. Raspberry Pi can also be used to be the control computer. For the streaming server, you need a computer with VLC media player installed. The user need to have a phone with mobile hotspot capabilities. 

# Set up streaming server
1. Install VLC media player from the [VLC Official Site](https://www.videolan.org/).
2. With the VLC media player window open, click `Media` button on the top left corner. Then select `Stream...` option.
3. With the `Open Media` window open, click `Add...` button under the `File` tab. Then choose the music file you want to stream. A file with long time duration is recommended as VLC does not support streaming list of music files.
4. After selecting the music file, click `Stream` button on the bottom right corner. Then click `Next` button again until you see the `Destination Setup` window.
5. In the `Destination Setup` window, select `HTTP` as the `New destination`. Then click `Add` button. If you want listen to the stream on the server as well, check the `Display locally` box. Under the `HTTP` tab, set the `Port` number. Do not change the `Path`. Then click `Next` button.
6. In the `Transcoding Options` window, check `Activate Transcoing` box. Select `Audio - MP3` or `Audio - FLAC` as the profile depending on the original music file format. Then click `Next` button.
7. In the `Option Setup` window, do not change anything, click `Stream` button on the bottom right corner.
8. Then streaming server is now set up.

# Set up control server
1. Download the `Server.py` file.
2. Run the script with `python3 Server.py -p [port number] -a [address of streaming server, e.g. http://192.168.0.100:8080] -n [number of Raspberry Pis in the network] -s [SSID of the mobile hotspot]`. If there is no dependency error, you should see `waiting for connection` shown in the terminal. 
3. Then we need to setup the 3 Raspberry Pis as clients.

# Set up clients
1. Before running the Python script, you need to run `pip3 install python-vlc` and `pip3 install rssi` to install the 2 dependencies.
2. You should follow [github page](https://github.com/jvillagomez/rssi_module/issues/1) to modify one error in the `rssi` module.
3. Download the `Raspberry.py` file to the Raspberry Pis.
4. Run the script with `python3 Raspberry.py -s [server address] -p [port number] -n [name for this client]`. 
5. Ideally, when the control server and Raspberry Pi are under the same network, you should see `allow connection from IP_ADDRESS?` message on the control server terminal. You should check the prompted ip address with the actual Raspberry Pi address. To allow connection, type `y` in the control server terminal.
6. Repeat the above procedures to connect all clients to the control server.
7. After all clients are setup, the control server will send command to the clients to control the audio playback. You should hear the music from streaming server with the headphone connected to the clients. Only one device will play the music at the same time.
