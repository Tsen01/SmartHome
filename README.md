# SmartHome

In this project, we built a home automation system where an ESP32 microcontroller uses three types of sensors (pressure, ultrasonic, infrared temperature) to detect human activity and automatically provide lighting.  
Beyond automatic control, users can monitor the light status from a web interface and control the lights remotely via Discord. When the lights are turned on while users are marked as "out", the Discord Bot automatically sends notification messages with an image of the triggered lights. 


## System Architecture

### Perception Layer
Three types of sensors are used to detect environment and human activity:
- **Pressure Sensor**: Detects whether someone is sitting or stepping on a surface.  
- **Ultrasonic Sensor**: Detects distance changes to determine if someone is moving nearby.  
- **Infrared Temperature Sensor**: Detects human body heat or infrared signals.

### Network Layer
- Uses **Wi-Fi** to upload sensor data to **Firebase Realtime Database**.  
- Firebase acts as a database to synchronize data between the web interface and the Discord Bot.

### Application Layer
- Users can view the lighting status at home through a **web interface** and **remotely control lights**.  
- **Discord Bot** capabilities:  
  - Control lights remotely directly via Discord using slash commands:  
    - `/light on` — Turn on the lights.
    - `/light off` — Turn off the lights.
    - `/light status` — Check the current light status.
    - `/goout` — Mark yourself as out of home.
  - If a user is marked as "out" using /goout, the bot sends a DM with an image of the light that was triggered (entrance or living room).


## Key Features
- Sensors automatically detect human activity and intelligently decide whether to turn on lights.  
- Real-time data synchronization with Firebase.  
- Discord Bot provides cross-platform control and notifications.  
- Intuitive web interface for easy remote control.


## Technologies Used
| Layer | Function | Technology |
|-------|---------|-----------|
| Perception Layer | Detect human activity | ESP32 + Pressure Sensor + Ultrasonic Sensor + Infrared Temperature Sensor |
| Network Layer | Cloud data storage | Firebase Realtime Database |
| Application Layer | Remote monitoring and control | HTML / JavaScript / Discord Bot API |


## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
