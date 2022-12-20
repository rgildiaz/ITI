# Factory Reset and Configuration: Aruba 3810M Switch, SEL 2730M Switch, and Cisco 4321 Router

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

> Once the PuTTY terminal window boots, it may appear blank. Pressing RETURN should show the command line prompt, which in my case is ``Aruba-3810M-48G-PoEP-1-slot#``. If this appears, you are connected correctly.

To complete the minimal configuration through the console port, follow these instructions:

1. Type the ``setup`` command to enter the Switch Setup screen.
2. Use the TAB key or the arrow keys to navigate to the ``Manager Password`` field. Input a new password and confirm the same password on the following line.
3. Navigate to the ``IP Config`` field and use the spacebar to select the ``Manual`` option.
4. Navigate to the ``IP Address`` field and set a static IP address. Set the appropriate subnet mask on the next line. This information will apply to the default VLAN. I set mine to:

```
IP Address: 192.168.0.100
Subnet Mask: 255.255.255.0
```

5. Press ``ENTER`` and then ``S`` to save.

Once you have set an IP address in this way, the switch can be managed via the browser-based GUI by navigating to its address:

1. Connect the Aruba and your computer to a switch.
2. Open a web browser and search for the IP address that you set via the serial console.
3. To manage the switch login using username: manager and the password set during the setup process.

### SSH Access

SSH is enabled by default on this Aruba switch. You can SSH from a connected computer via the command line using this command, replacing the IP address with the one set during the above setup:

```
ssh manager@192.168.0.100
```

### Navigation

Once logged in with the manager account, you should see the following:

```
Aruba-3810M# 
```

The ``#`` indicates the manager context, from which the switch's configuration can be changed. To exit the manager context and enter the operator context, which cannot change configurations, use ``CTRL + Z`` or the ``exit`` command. To enter the manager context from the operator context, use the ``enable`` command:

```
Aruba-3810M> enable
Username: manager
Password:
Your previous successful login (as manager) was on 2022-07-06 15:51:30
 from 192.168.0.107
Aruba-3810M#
```

To enter the configuration terminal from the manager context, use the following command:

```
Aruba-3810M# config terminal
Aruba-3810M(config)# 
```

The ``(config)#`` indicates that this is the configuration terminal.

Another navigation option is the menu, which can be accessed with the ``menu`` command:

```
Aruba-3810M# menu
```

```
Aruba-3810M                                                 6-Jul-2022  16:03:51
===========================- TELNET - MANAGER MODE -============================
                                   Main Menu

   1. Status and Counters...
   2. Switch Configuration...
   3. Console Passwords...
   4. Event Log
   5. Command Line (CLI)
   6. Reboot Switch
   7. Download OS
   8. Run Setup
   0. Logout







Provides the menu to display configuration, status, and counters.

To select menu item, press item number, or highlight item and press <Enter>.
```

### Copy a config file from/to a TFTP server

If a tftp server is setup and on the same network as the Aruba 3810M, you can copy a config file to and from the server using the following command from the switch's configuration terminal:

```
Aruba-3810M# copy tftp config "config1" 192.168.0.105 "testconfig.pcc"
```

``copy tftp``: copy a file from a tftp server.
``config "config1"``: expect the file to be of type ``config`` and copy the file's contents to ``config1``.
``192.168.0.105``: the IP of the tftp server.
``"testconfig.pcc"``: the name of the file to be copied.

The same command can also be used to copy a config file to the server. This will only work if "testconfig.pcc" doesn't exist on the server. In this case:
``config "config1"``: copy the configuration ``config1``
``"testconfig.pcc"``: to a new file called ``testconfig.pcc``.

## SEL 2730M Switch

To perform a factory reset on the SEL 2730M switch, follow the steps below:
> Turn off power to your SEL-2730M, insert a tool such as a straightened paper clip into the pinhole reset hole above Port 2 on the rear panel, and press the recessed reset button. Holding the button depressed, apply power. After five seconds, release the recessed reset button.

> Wait for the green ENABLED LED on the front panel to illuminate, indicating that your SEL-2730M has reset to factory-default settings and is ready. ETH F will be enabled, the Captive Port feature will be on, and the IP address for the unit will be 192.168.1.2. You can access the Commissioning page by entering a hostname, such as selinc.com, or you can browse directly to the IP address for the unit at <https://192.168.1.2>

- These instructions were copied from the [SEL 2730M Instruction Manual](https://selinc.com/products/2730M/docs/).

After the device has been reset, it can be configured through the web portal. Make sure the device is connected to your network via its ETH F port, located on the right side of the front panel. Then, navigate to its default IP address, 192.168.1.2.

The SEL-2730M is not capable of SSH.

## Cisco 4321 Router

The Cisco 4321 Integrated Services Router that I am using is running Cisco IOS XE Software, Version 16.09.02. Documentation and other information can be found on [Cisco's product page](https://www.cisco.com/c/en/us/support/routers/4321-integrated-services-router/model.html).

### Password and Secret Recovery and Reset

You may find that you do not know the password or secret for your device, locking you out of changing any configurations. These can be reset by connecting via one of the management ports, located on the left side of the back of the switch. To complete these steps, I used the mini USB connector to connect the router to my laptop.

#### Setup

I will use [PuTTY](https://www.putty.org/) as a [VT 100 terminal](https://en.wikipedia.org/wiki/VT100) emulator. To setup PuTTY for the connection, follow these steps:

1. Find the name of the serial port which is connected.
    1. Open the Device Manager
    2. In the menu bar at the top of the window, click "View" &rarr; "Show hidden devices".
    3. Open the drop-down labeled "Ports (COM & LPT)"
    4. The name of the port is inside the parentheses at the end of the entry: "USB Serial Device (COM1)" means the port name is "COM1".
2. Configure PuTTY for connection.
    1. In the menu at the left side of the PuTTY window, select "Serial", located in the "Connection" submenu. Set the following:
        - Serial line connect to: COM1
        - Speed (baud): 9600
        - Data bits: 8
        - Stop bits: 1
        - Parity: none
        - Flow control: XON/XOFF
3. Click the "Open" button at the bottom of the window to launch the terminal window.

Once connected via serial port, attempt to check the configuration register value using the ``show version`` command. Write down this value for later:

```
cisco> show version
```

```
...
0K bytes of WebUI ODM Files at webui:.

Configuration register is 0x2012
```

For more information, refer to this article from Cisco about [replacing or recovering a lost password](https://www.cisco.com/c/en/us/td/docs/routers/access/4400/troubleshooting/guide/isr4400trbl/isr4400trbl02.html).

### Factory Reset

If you have administrator access to the router and can connect via your network, follow the instructions below. Otherwise, [start by recovering and resetting the password and secret via a serial connection](#password-and-secret-recovery-and-reset).

```
cisco# factory-reset all
```

Refer to [Cisco's documentation about factory resetting 4000 series routers](https://www.cisco.com/c/en/us/td/docs/routers/access/4400/software/configuration/xe-16-12/isr4400swcfg-xe-16-12-book/m_perform_factory_reset_isr.html) for more information. Be aware that many of the instructions in this guide did not work for me, as it was written for IOS XE version 16.12.xx while I am on 16.09.02.

### Copy to/from TFTP Server

To copy a startup config from the tftp server, use the following command:

```
cisco# copy tftp: startup-config
Address or name of remote host []? 192.168.0.105
Source filename []? cisco-confg
Destination filename [startup-config]?
Accessing tftp://192.168.0.105/cisco-confg...
Loading cisco-confg from 192.168.0.105 (via GigabitEthernet0): !!
[OK - 349559 bytes]

349559 bytes copied in 11.175 secs (31280 bytes/sec)
```

A simple way to copy a configuration to the TFTP server is the ``write net`` command:

```
cisco# write net
This command has been replaced by the command:
         'copy system:/running-config <url>'
Address or name of remote host []? 192.168.0.105
Destination filename [cisco-confg]?
Write file tftp://192.168.0.105/cisco-confg? [confirm]

!! [OK]
```

As the warning message states, ``write net`` has been replaced:

```
cisco# copy system:/running-config tftp: all
Address or name of remote host []? 192.168.0.105
Destination filename [cisco-confg]?
!!!
349559 bytes copied in 0.496 secs (704756 bytes/sec)
```
