# Factory Reset Aruba 3810M Switch, SEL 2730M Switch, and Cisco 4321 Router

## Aruba 3810M Switch
### Factory Reset
To reset the Aruba 3810M, I followed the instructions on page 94 of [this Installation and Getting Started Guide](https://www.arubanetworks.com/techdocs/hardware/switches/3810/IGSG/3810_igsg.pdf). Specifically, I used these instructions:

1. Using pointed objects, simultaneously press both the Reset and Clear buttons on the front of the switch.
2. Continue to press the Clear button while releasing the Reset button.
3. When the Global Status LED begins to fast flash orange (after approximately 5 seconds), release the Clear button.
4. The switch will then complete its boot process and begin operating with its configuration restored to the factory default settings.

### Initial Configuration
After restoring the switch to factory-defaults, it has no IP address, subnet mask, or password. Because of this, it can only be managed through a direct console connection. To access the serial console, connect a micro USB &rarr; USB-A cable to the micro USB port on the right side of the front of the switch, labeled "Console Ports". Connect the USB-A side of the cable to a computer which has [PuTTY](https://www.putty.org/) installed. PuTTY will act as a serial console emulator since this serial micro USB port expects to send information to a [VT 100 terminal](https://en.wikipedia.org/wiki/VT100). 

To setup PuTTY for this purpose in Windows 10, follow the steps below:
1. Find the name of the serial port which is connected.
    1. Open the Device Manager
    2. In the menu bar at the top of the window, click "View" &rarr; "Show hidden devices".
    3. Open the drop-down labeled "Ports (COM & LPT)"
    4. The name of the port is inside the parentheses at the end of the entry: "USB Serial Device (COM3)" means the port name is "COM3".
2. Configure PuTTY for connection.
    1. Launch PuTTY and change the "Connection Type" radio button selection to "Serial".
    2. Edit the "Serial line" text box above these buttons to the name of the serial port interface. In my case, this would be "COM3".
    3. Make sure the speed is between 1200 and 115200. This number is equivalent to the baud rate.
    4. In the menu at the left of the window, open the "Serial" submenu, which is nested within "Connection". Ensure that:
        - data bits is set to 8,
        - stop bits is set to 1, 
        - parity is set to none, and 
        - flow control is set to "XON/XOFF".
3. Click the "Open" button at the bottom of the window to launch the terminal window.

> Once the PuTTY terminal window boots, it may appear blank. Pressing RETURN should show the command line prompt, which in my case is ``Aruba-3810M-48G-PoEP-1-slot# ``. If this appears, you are connected correctly.

To complete the minimal configuration through the console port, follow these instructions:
1. Type the ``setup`` command to enter the Switch Setup screen.
2. Use the TAB key or the arrow keys to navigate to the ``Manager Password`` field. Input a new password and confirm the same password on the following line.
3. Navigate to the ``IP Config`` field and use the spacebar to select the ``Manual`` option.
4. Navigate to the ``IP Address`` field and set a static IP address. Set the appropriate subnet mask on the next line.
5. Press ``ENTER`` and then ``S`` to save.

Once you have set an IP address in this way, the switch can be managed via the browser-based GUI by navigating to its address:
1. Connect the Aruba and your computer to a switch.
2. Open a web browser and search for the IP address that you set via the serial console.


### Copy a config file from a tftp server
```
Aruba-3810M# copy tftp config "config1" 192.168.0.105 "testconfig.pcc"
```

``copy tftp``: copy a file from a tftp server.
``config "config1"``: expect the file to be of type ``config`` and copy the file's contents to ``config1``.
``192.168.0.105``: the IP of the tftp server.
``"testconfig.pcc"``: the name of the file to be copied.

## SEL 2730M Switch

## Cisco 4321 Router