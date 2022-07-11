# Testing 10G SFP+ Bidirectional Transceivers
This page will document the process I used to test a pair of 10G Bidi's using a simple network. For a full list of equipment used, see the last section about [my equipment & other notes](#equipment--other-notes).

#### Contents:
- [Switch Setup](#switch-setup)
- [Network Architecture & Configuration](#network-architecture--configuration)
- [iPerf & Testing](#iperf--testing)
- [Troubleshooting & Workarounds](#troubleshooting--workarounds)
- [Equipment & Other Notes](#equipment--other-notes)

---

## Switch Setup
To begin setting up for this process, configure the switches. In my case, I used a pair of [Aruba 3810M switches](#equipment--other-notes) each outfitted with a [JL083A expansion module for SFP+](#equipment--other-notes). To configure a new or factory reset switch, follow the steps below.

### Initial Configuration
A factory-default switch can only be managed through a direct console connection. To access the serial console, connect a micro USB &rarr; USB-A cable to the micro USB port on the right side of the front of the switch, labeled "Console Ports". Connect the USB-A side of the cable to a computer which has [PuTTY](https://www.putty.org/) installed. PuTTY will act as a serial console emulator since this serial micro USB port expects to send information to a [VT 100 terminal](https://en.wikipedia.org/wiki/VT100). 

To setup PuTTY for this purpose in Windows 10, follow the steps below:
1. Find the name of the serial port which is connected.
    1. Open the Device Manager
    2. In the menu bar at the top of the window, click "View" &rarr; "Show hidden devices".
    3. Open the drop-down labeled "Ports (COM & LPT)"
    4. The name of the port is inside the parentheses at the end of the entry: "USB Serial Device (COM3)" means the port name is "COM3".
2. Configure PuTTY for connection.
    1. In the menu at the left side of the PuTTY window, select "Serial", located in the "Connection" submenu. Set the following:
        - Serial line connect to: COM3
        - Speed (baud): 9600
        - Data bits: 8
        - Stop bits: 1
        - Parity: none
        - Flow control: XON/XOFF
3. Click the "Open" button at the bottom of the window to launch the terminal window.

> Once the PuTTY terminal window boots, it may appear blank. Pressing RETURN should show the command line prompt, which in my case is ``Aruba-3810M-48G-PoEP-1-slot# ``. If this appears, you are connected correctly.

To complete the minimal configuration through the console port, follow these instructions:
1. Type the ``setup`` command to enter the Switch Setup screen.
2. Use the TAB key or the arrow keys to navigate to the ``Manager Password`` field. Input a new password and confirm the same password on the following line.
3. Navigate to the ``IP Config`` field and use the spacebar to select the ``Manual`` option.
4. Navigate to the ``IP Address`` field and set a static IP address. Set the appropriate subnet mask on the next line. This information will apply to the default VLAN. I set mine to:
```
IP Address: 192.168.2.2
Subnet Mask: 255.255.255.0
```
5. Press ``ENTER`` and then ``S`` to save.

Once you have set an IP address in this way, the switch can be managed via the browser-based GUI by navigating to its address:
1. Connect a computer to the same network as the Aruba.
2. Open a web browser and search for the IP address that you set via the serial console.
3. Login using the username and password set during the setup process.

### SSH Access
SSH is enabled by default on this Aruba switch. You can SSH from a connected computer via the command line using this command, replacing the IP address with the one set during the above setup:
```
ssh manager@192.168.2.2
```

Make sure to follow these steps for both switches which will be used. When setting an IP for the second switch I chose ``192.168.2.3``.

### Connect the Switches
Once both switches have been configured, connect them using the bidi's and a fiber cable. Make sure to use bidi's which are compatible with the switches you are using. After inserting each bidi into each switch, it should blink green within ~5 seconds, indicating that the switch is compatible and the bidi is ready for a connection.

Since the bidi's accept an LC connection, I used a 30 m ST-ST cable, two ST-ST adapters, and two ST-LC cables to connect them. Since they have been configured on the same subnet, they should be able to communicate accross the fiber connection.

> See [troubleshooting & workarounds] if this isn't working.

## Network Architecture & Configuration
Now that the switches have been configured, we can begin setting up a network on them. I setup my network using 6 [Intel NUC](#equipment--other-notes)'s, one of which acts as a DHCP server, and a 6-port [logic supply](#equipment--other-notes).

### DHCP
To start, configure the DHCP server. Due to a previous project, I already had one configured using Ubuntu Server 20.04. To configure a similar server, follow the steps below:
1. Install Ubuntu Server 20.04 on an Intel NUC. I used a bootable USB installer.
2. There is only one necessary package for this project, ``isc-dhcp-server``:
```
sudo apt-get install isc-dhcp-server
```
3. Configure a static IP:
```
sudo nano /etc/netplan/01-netcfg.yaml
```
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eno1:
      dhcp4: no
      addresses:
        - 192.168.2.10/24
      gateway4: 192.168.2.1
      nameservers:
        addresses: [1.1.1.1, 1.0.0.1]
```
> make sure to change ``eno1`` to the correct ethernet port name.
```
sudo netplan apply
```
4. Configure the DHCP server:
```
sudo nano /etc/dhcp/dhcpd.conf
```
```yaml
# make sure to update the ip and mac addresses as appropriate.
subnet 192.168.2.0 netmask 255.255.255.0 {
        # I set a range of .106 to .200, as this far exceeds the < 15 devices I plan on testing. 
        range 192.168.2.106 192.168.2.200;
        option routers 192.168.2.1;
        default-lease-time 3600;
        max-lease-time 86400;
        next-server 192.168.2.10;
}

host desktop {
        hardware ethernet 94:c6:91:a1:1f:a5;
        fixed-address 192.168.2.10;
}

ddns-update-style none;

authoritative;
```
5. Restart the server and check its status.
```
sudo systemctl restart isc-dhcp-server
sudo systemctl status isc-dhcp-server
```

At this point, the DHCP server should be up and running. You should see an output from the status message something like this:
```
● isc-dhcp-server.service - ISC DHCP IPv4 server
     Loaded: loaded (/lib/systemd/system/isc-dhcp-server.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2022-07-11 13:57:54 UTC; 6h ago
       Docs: man:dhcpd(8)
   Main PID: 902 (dhcpd)
      Tasks: 4 (limit: 38297)
     Memory: 6.8M
     CGroup: /system.slice/isc-dhcp-server.service
             └─902 dhcpd -user dhcpd -group dhcpd -f -4 -pf /run/dhcp-server/dhcpd.pid -cf /etc/dhcp/dhcpd.conf eno1

Jul 11 20:01:28 server dhcpd[902]: DHCPACK on 192.168.2.106 to 8c:04:ba:35:4b:76 (DESKTOP-H2PRVNN) via eno1
Jul 11 20:03:01 server dhcpd[902]: DHCPREQUEST for 192.168.2.111 from 78:d0:04:26:19:0f (logic) via eno1
Jul 11 20:03:01 server dhcpd[902]: Wrote 0 deleted host decls to leases file.
Jul 11 20:03:01 server dhcpd[902]: Wrote 0 new dynamic host decls to leases file.
Jul 11 20:03:01 server dhcpd[902]: Wrote 21 leases to leases file.
Jul 11 20:03:01 server dhcpd[902]: DHCPACK on 192.168.2.111 to 78:d0:04:26:19:0f (logic) via eno1
Jul 11 20:04:11 server dhcpd[902]: DHCPREQUEST for 192.168.2.115 from 78:d0:04:26:19:0a (logic) via eno1
Jul 11 20:04:11 server dhcpd[902]: DHCPACK on 192.168.2.115 to 78:d0:04:26:19:0a (logic) via eno1
Jul 11 20:04:33 server dhcpd[902]: DHCPREQUEST for 192.168.2.127 from 94:c6:91:a2:2a:db (nuc3) via eno1
Jul 11 20:04:33 server dhcpd[902]: DHCPACK on 192.168.2.127 to 94:c6:91:a2:2a:db (nuc3) via eno1
```

### DHCP Clients
Now that the DHCP server has been setup, other interfaces connected to the network will be automatically assigned an IP. In my case, I connected 5 more NUC's as well as all 6 ports of the logic supply I used. I plan on configuring the logic supply interfaces as the iPerf servers and all the NUC's as iPerf clients.

I installed the same release of Ubuntu Server 20.04 on all the other devices I used for this. The last step before testing the network is to install [iPerf](https://iperf.fr/) on all the devices. Since I am working without a direct internet connection on all the devices used, I copied the appropriate [Ubuntu binaries] to a flash drive and manually installed in on each device:
1. Download the [iPerf Ubuntu binaries](https://iperf.fr/iperf-download.php#ubuntu) to a computer which has network connection. I used iPerf_3.9.deb + libiperf0_3.9-1.deb + libsctp1_1.0.18+dfsg-1.deb. Copy the files to a flash drive. 
2. Connect the flash drive to one of the networked computers. Use ``fdisk`` to find the name of the drive, and then mount it:
```
sudo fdisk -l
```
```
Disk /dev/loop1: 69.9 MiB, 73277440 bytes, 143120 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes

...

Disk /dev/sdb: 29.9 GiB, 32080200192 bytes, 62656641 sectors
Disk model: Flash Drive FIT
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x1dee8e35

Device     Boot Start      End  Sectors  Size Id Type
/dev/sdb1          63 62656640 62656578 29.9G  7 HPFS/NTFS/exFAT
```
I like creating a USB directory:
```
sudo mkdir /media/USB
sudo mount /dev/sdb1 /media/USB
cd /media/USB
```
Make sure these files are in the USB directory:
```
iperf3_3.9-1_amd64.deb   libiperf0_3.9-1_amd64.deb   libsctp1_1.0.18+dfsg-1_amd64.deb
```
3. Once mounted, install the packages. The order of installation matters.
```
sudo dpkg -i libsctp1_1.0.18+dfsg-1_amd64.deb
sudo dpkg -i libiperf0_3.9-1_amd64.deb
sudo dpkg -i iperf3_3.9-1_amd64.deb
```

Now, iPerf should be installed. You should see the help file when using the ``iperf3`` command now:
```iperf3```
```
iperf3: parameter error - must either be a client (-c) or server (-s)

Usage: iperf3 [-s|-c host] [options]
       iperf3 [-h|--help] [-v|--version]

Server or Client:
  -p, --port      #         server port to listen on/connect to
  -f, --format   [kmgtKMGT] format to report: Kbits, Mbits, Gbits, Tbits
...
```

## iPerf & Testing

## Troubleshooting & Workarounds

## Equipment & Other Notes