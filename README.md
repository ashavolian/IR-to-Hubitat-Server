```text
██╗██████╗     ████████╗ ██████╗     ██╗  ██╗██╗   ██╗██████╗ ██╗████████╗ █████╗ ████████╗
██║██╔══██╗    ╚══██╔══╝██╔═══██╗    ██║  ██║██║   ██║██╔══██╗██║╚══██╔══╝██╔══██╗╚══██╔══╝
██║██████╔╝       ██║   ██║   ██║    ███████║██║   ██║██████╔╝██║   ██║   ███████║   ██║   
██║██╔══██╗       ██║   ██║   ██║    ██╔══██║██║   ██║██╔══██╗██║   ██║   ██╔══██║   ██║   
██║██║  ██║       ██║   ╚██████╔╝    ██║  ██║╚██████╔╝██████╔╝██║   ██║   ██║  ██║   ██║   
╚═╝╚═╝  ╚═╝       ╚═╝    ╚═════╝     ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   
```
# 💡 IR to Hubitat Mapper

A web interface designed for the Raspberry Pi Zero W (or any other Raspberry Pi with wifi support) for mapping IR remote controls to Hubitat device commands. This application allows you to teach IR commands and link them to specific Hubitat device actions ✨

## ⭐ Features

- Map IR remote buttons to Hubitat device commands
- Support for multiple remotes
- Real-time IR command teaching
- Easy-to-use web interface
- Support for device parameters

## 📸 Screenshots

### Main Interface
<img width="400" src="https://github.com/user-attachments/assets/b3e9a74c-f955-4242-8b07-5c9f80fdc63a" />

### Adding New Mapping
<img width="400" src="https://github.com/user-attachments/assets/0c5379b5-8e7e-4401-882a-9ab4f36b199e" />

### Current Mappings View
<img width="400" src="https://github.com/user-attachments/assets/5cb509da-61f3-4901-916b-b82b84b1ce99" />

## 🚀 Installation

1. Clone the repository:

```bash
git clone https://github.com/ashavolian/ir-to-hubitat-mapper.git
cd ir-to-hubitat-mapper
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your Hubitat settings in `app.py`:

```python
HUBITAT_IP = "your.hubitat.ip"
ACCESS_TOKEN = "your-access-token"
```

4. Ensure LIRC is installed and configured:
```bash
sudo apt-get install lirc
```


## 🔧 LIRC Configuration

1. Configure your IR receiver:
[Insert picture of IR receiver setup]

2. Test your LIRC setup:
```bash
irw
```
<img width="280" alt="Screenshot 2025-01-27 at 7 22 16 PM" src="https://github.com/user-attachments/assets/8eb2d0ed-26e7-4390-8656-1d69302083fa" />

## 🛠️ Hardware Setup

### Required Components
- Raspberry Pi (any model)
- IR receiver (TSOP38238 or similar)
- 3 jumper wires
- Optional: IR LED for transmitting (future feature)
  
I used [these parts](https://www.amazon.com/gp/product/B08X2MFS6S?ie=UTF8&psc=1)

### IR Receiver Wiring
Connect your IR receiver to the Raspberry Pi:
1. VCC (Power) → Pin 1 (3.3V)
2. GND (Ground) → Pin 6 (Ground)
3. OUT (Signal) → Pin 18 (GPIO18)

[Insert wiring diagram image here]

## ⚙️ Raspberry Pi Configuration

### 1. Enable IR Support
Add these lines to `/boot/config.txt`:
```bash
# IR receiver on GPIO18
dtoverlay=gpio-ir,gpio_pin=18
```

### 2. Configure LIRC
Update `/etc/lirc/lirc_options.conf`:
```bash
driver          = default
device          = /dev/lirc0
```

### 3. Create LIRC Service
Create `/etc/systemd/system/ir-to-hubitat.service`:
```ini
[Unit]
Description=IR to Hubitat Mapper
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/your/app.py
WorkingDirectory=/path/to/your/project
User=pi
Group=pi
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Start Services
```bash
# Enable and start LIRC
sudo systemctl enable lircd
sudo systemctl start lircd

# Enable and start IR to Hubitat
sudo systemctl enable ir-to-hubitat
sudo systemctl start ir-to-hubitat
```

### 5. Verify Setup
```bash
# Check LIRC status
sudo systemctl status lircd

# Test IR reception
mode2 -d /dev/lirc0
```
Point a remote at your IR receiver and press buttons. You should see output indicating IR signals are being received.

### Troubleshooting Hardware
1. No IR signals detected:
   - Check wiring connections
   - Verify voltage with multimeter
   - Try different GPIO pin and update config
   - Ensure IR receiver is not in direct sunlight

2. Permission issues:
```bash
sudo usermod -a -G gpio pi
sudo usermod -a -G video pi
```

3. Hardware conflicts:
   - Disable audio if using GPIO18: `dtparam=audio=off` in `/boot/config.txt`
   - Check for conflicting GPIO usage

## 📡 Hubitat Device Setup

### Prerequisites
- A Hubitat Elevation hub
- Admin access to your Hubitat dashboard
- The Maker API app installed on your Hubitat

### Step 1: Install the Maker API
1. Go to your Hubitat dashboard
2. Click on "Apps" in the left sidebar
3. Click "Add Built-In App"
4. Select "Maker API" from the list
5. Enable OAuth
6. Select the devices you want to control
7. Save the configuration
8. Note down your:
   - Hub IP address
   - Access Token
   - App ID

### Step 2: Add Your Devices
1. Go to "Devices" in the left sidebar
2. Click "Add Virtual Device"
3. Fill in the following:
   - Name: Choose a meaningful name
   - Type: Select appropriate device type
4. Click "Save Device"

### Step 3: Configure the App
Add your Hubitat credentials to the configuration file `config.py`:
```python
# Hubitat Connection Settings
HUBITAT_IP = "192.168.1.100"  # Replace with your hub's IP address
HUBITAT_ACCESS_TOKEN = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # Your Maker API access token
HUBITAT_APP_ID = "1234"  # Your Maker API app ID
```

### Supported Device Types
- Switches
- Dimmers
- Color Bulbs
- Motion Sensors
- Contact Sensors
- Temperature Sensors

### Testing Your Setup
1. Open your Hubitat dashboard
2. Go to "Apps" > "Maker API"
3. Click "Show Example URLs"
4. Test a device command using the provided endpoints

### Troubleshooting
- Ensure your computer is on the same network as your Hubitat hub
- Verify your access token has the correct permissions
- Check that the selected devices are enabled in the Maker API
- Confirm your firewall isn't blocking the connection

For more detailed Hubitat documentation, visit the [Hubitat Community Wiki](https://docs.hubitat.com/).

## 📺 Example Remote Configurations (easily learnable with the Sofabaton U2)

The following are two example remote configurations that you can use as a starting point. Save these in separate files under `/etc/lirc/lircd.conf.d/`.

### Remote 1 (RC5 Protocol)
Save as `/etc/lirc/lircd.conf.d/remote1.lircd.conf`:

```text
begin remote

  name  remote1
  bits           13
  flags RC5|CONST_LENGTH
  eps            30
  aeps          100

  one           951   830
  zero          951   830
  plead         974
  gap          114060
  toggle_bit      2

  begin codes
      KEY_POWER          0x190E
      KEY_MUTE           0x110D
      KEY_VOLUMEUP       0x1110
      KEY_VOLUMEDOWN     0x1911
      KEY_CHANNELUP      0x1926
      KEY_CHANNELDOWN    0x1127
      KEY_BACK           0x191D
      KEY_HOME           0x1921
      KEY_INFO           0x1925
      KEY_INPUT          0x113E
      KEY_UP             0x1929
      KEY_DOWN           0x1928
      KEY_LEFT           0x110F
      KEY_RIGHT          0x112A
      KEY_OK             0x110B
      KEY_RED            0x113B
      KEY_GREEN          0x192B
      KEY_YELLOW         0x1932
      KEY_BLUE           0x1933
      KEY_1              0x1901
      KEY_2              0x1102
      KEY_3              0x1903
      KEY_4              0x1904
      KEY_5              0x1105
      KEY_6              0x1906
      KEY_7              0x1907
      KEY_8              0x1108
      KEY_9              0x1909
      KEY_0              0x1100
      KEY_PLAY           0x1135
      KEY_PAUSE          0x192F
      KEY_STOP           0x1136
      KEY_RECORD         0x113D
      KEY_FASTFORWARD    0x1120
      KEY_REWIND         0x1923
      KEY_OPTION         0x110A
  end codes

end remote
```

### Remote 2 (RC6 Protocol - Philips TV)
Save as `/etc/lirc/lircd.conf.d/remote2.lircd.conf`:

```text
begin remote

  name  remote2            # PHILIPS_26PFL5604H
  bits            8
  flags RC6|CONST_LENGTH
  eps            30
  aeps          100

  header       2718   844
  one           478   408
  zero          478   408
  pre_data_bits   13
  pre_data       0xEFF
  gap          106540
  min_repeat      1
  toggle_bit_mask 0x10000
  rc6_mask    0x10000

      begin codes
          KEY_POWER                0xF3                      #  Was: Power
          KEY_YELLOW               0x90                      #  Was: yellow
          KEY_GREEN                0xB4
          KEY_BLUE                 0xC3
          KEY_RED                  0xC7
          KEY_HOME                 0xAB                      #  Was: Home
          KEY_OPTION               0xBF                      #  Was: OPTIONS
          KEY_UP                   0xA7                      #  Was: up
          KEY_LEFT                 0xA5                      #  Was: left
          KEY_OK                   0xA3                      #  Was: OK
          KEY_RIGHT                0xA4                      #  Was: right
          KEY_DOWN                 0xA6                      #  Was: down
          KEY_BACK                 0xF5                      #  Was: BACK
          KEY_INFO                 0xF0                      #  Was: INFO
          KEY_REWIND               0xD4                      #  Was: <<
          KEY_PLAY                 0xD3                      #  Was: Play
          KEY_PAUSE                0x0B
          KEY_FORWARD              0xD7                      #  Was: >>
          KEY_STOP                 0xCE                      #  Was: Stop
          KEY_RECORD               0xC8                      #  Was: Record
          KEY_VOLUMEUP             0xEF                      #  Was: Vol+
          KEY_VOLUMEDOWN           0xEE                      #  Was: Vol-
          KEY_MUTE                 0xF2                      #  Was: Mute
          KEY_CHANNELUP            0xDF                      #  Was: P+
          KEY_CHANNELDOWN          0xDE                      #  Was: P-
          KEY_1                    0xFE                      #  Was: 1
          KEY_2                    0xFD                      #  Was: 2
          KEY_3                    0xFC                      #  Was: 3
          KEY_4                    0xFB                      #  Was: 4
          KEY_5                    0xFA                      #  Was: 5
          KEY_6                    0xF9                      #  Was: 6
          KEY_7                    0xF8                      #  Was: 7
          KEY_8                    0xF7                      #  Was: 8
          KEY_9                    0xF6                      #  Was: 9
          KEY_0                    0xFF                      #  Was: 0
      end codes

end remote
```

## 🔌 IR Blaster Setup

### Additional Components
- IR LED (940nm recommended)
- NPN transistor (2N2222 or similar)
- 220Ω resistor for GPIO
- 47Ω resistor for LED
- Jumper wires

### IR Blaster Wiring
Connect the IR blaster circuit to the Raspberry Pi:
1. ground → gnd
2. 3.3V (Pin 1) → vcc
3. GPIO17 → dat


### Update Pi Configuration
Add these lines to `/boot/config.txt`:
```bash
# IR receiver on GPIO18
dtoverlay=gpio-ir,gpio_pin=18
# IR transmitter on GPIO17
dtoverlay=gpio-ir-tx,gpio_pin=17
```

### Testing IR Blaster
1. Install IR testing tools:
```bash
sudo apt-get install ir-ctl
```

2. Create a test signal:
```bash
# Generate NEC protocol signal (common for many devices)
ir-ctl -d /dev/lirc0 --send=pulse.txt
```

3. Basic test file (`pulse.txt`):
```text
carrier 38000
space 9000
pulse 4500
space 4500
pulse 560
space 560
pulse 560
```

4. Verify transmission:
```bash
# Send test signal
ir-ctl -d /dev/lirc0 --send=pulse.txt

# For debugging
ir-ctl -d /dev/lirc0 --features
```

### Multiple IR LED Setup
For better coverage, you can connect multiple IR LEDs in parallel:
```text
                   ┌──── IR LED 1
3.3V ──┬── 47Ω ───┼──── IR LED 2
       │          └──── IR LED 3
       └── Transistor Collector
```
Note: When using multiple LEDs, you may need to adjust the resistor value or use individual resistors for each LED.

## 📖 Usage

1. Start the application:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://[your-server-ip]:5000
```

### 🎓 Teaching IR Commands
<img width="500" src="https://github.com/user-attachments/assets/ad2c6c6f-89ea-41e1-b3e3-06827bac0645" />

1. Select your remote
2. Choose the IR key
3. Click "Teach IR Command"
4. Press the button on your remote

### 🔗 Mapping Commands

<img width="400" src="https://github.com/user-attachments/assets/4283ccd9-c4f9-4b41-a1b3-16d4add9a4ea" />

1. Select the target Hubitat device
2. Choose the command
3. Add any required parameters
4. Click "Add Mapping"

## 🎮 SofaBaton U2 Integration

The SofaBaton U2 Universal Remote Control is an excellent choice for this project because:

1. It's pre-configured with a vast database of IR codes
2. Can learn new IR codes from existing remotes
3. Has built-in IR blasting capabilities
4. Connects via USB for easy integration

### Setting Up SofaBaton U2

1. **Physical Setup**:
   - Position the IR blaster where it can reach your devices (in my case this was right up against the ir blaster)

2. **Learning New Codes**:

The web interface makes it easy to teach new codes to your system:

1. Navigate to the "Learn IR" section in the web interface
2. Select "Start Learning Mode"
3. Point your existing remote at the SofaBaton U2
4. Press the button you want to learn
5. Name and save the command

### Benefits for Home Automation

- **Multiple Device Control**: One U2 can control multiple devices simultaneously
- **Wide Compatibility**: Works with most IR-controlled devices
- **Reliable Performance**: Strong IR signal for consistent device control
- **Cost-Effective**: Single device solution for multiple remote control needs
- **User-Friendly**: Web interface makes learning and managing IR codes simple

> **Tip**: The SofaBaton U2 is particularly useful for this project as it can both learn from your existing remotes and blast IR signals, all manageable through an intuitive web interface.

## 🔍 Troubleshooting

### 🐛 Common Issues

1. LIRC daemon issues:

```bash
sudo systemctl restart lircd
```

2. Permission problems:

```bash
sudo chmod 666 /dev/lirc0
```

## 🤝 Contributing

Contributions are welcome! Let's make this project awesome together! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

### In simple terms:
This is free software that anyone can use, study, share, and improve. However, if you modify and share this software, you must:
1. Make your source code available
2. License your modifications under the same GPL-3.0 license
3. Give credit to the original project

For the full license text, see the [LICENSE](LICENSE) file.

## 💖 Acknowledgments

Special thanks to:
- The amazing LIRC project team 🌟
- The wonderful Hubitat community 🏠
- The fantastic Flask framework developers 🌐

