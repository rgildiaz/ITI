# PXE Boot ShredOS

This document will walk through the processes I used to set up a PXE server to network boot ShredOS. I will cover the server setup in both [Ubuntu Server 20.04.4 LTS](https://releases.ubuntu.com/20.04/) and [SLAX](https://www.slax.org/). You can also find troubleshooting and workaround that might be useful. Finally, the last section contains information about the equipment I used as well as other notes.

While I setup the SLAX and Ubuntu servers in slightly different ways, either way should work on either operating system as the packages used are system-independent.

#### Contents:
- [Ubuntu Server 20.04.4](#ubuntu-server-20044)
- [SLAX Linux](#slax-linux)
- [Troubleshooting and Workarounds](#troubleshooting-and-workarounds)
- [Equipment and Other Notes](#equipment-and-other-notes)

---

## Ubuntu Server 20.04.4
While any Linux operating system should be able to follow the steps below to setup a server, Ubuntu is a good choice for this project since it is very well documented and supported. I began working from a fresh install of [Ubuntu Server 20.04.4 LTS](https://releases.ubuntu.com/20.04/) on an [Intel NUC](#equipment-and-other-notes).

### Setup
To begin, install the necessary packages:
```
sudo apt-get -y update && sudo apt-get -y upgrade
sudo apt-get -y install isc-dhcp-server tftpd-hpa pxelinux syslinux
```
``isc-dhcp-server`` will act as the DHCP server, and ``tftpd-hpa`` will be the TFTP server. ``pxelinux`` and ``syslinux`` provide the necessary files and functionality for PXE booting.

Also, it is nice to have a static IP address for the DHCP server. To do so, navigate to your ``/netplan/`` to change it:
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
        - 192.168.0.105/24
      gateway4: 192.168.0.1
      nameserver:
        addresses: [1.1.1.1,1.0.0.1]
```
I set this server's IP to ``192.168.0.105``. Make sure to change ``eno1`` to the name of the interface you will use to run the server. You can find this using:
```
ip a
```
In my case, I see:
```
1: lo: ...
...
2: eno1: <ND-CARRIER,BROADCAST,MULTICAST,UP> ...
```

The [NUC](#equipment)'s only have one ethernet port, which I have plugged into the network switch, so ``eno1`` is the name of the ethernet port that will be used for this.

### TFTP
The TFTP server will copy the bootloader and kernel to the client computer. To start, create a place to store the files which will be transferred:
```
sudo mkdir /tftpboot
```

If you are planning to boot a different operating system than ShredOS, populate the ``/tftpboot`` directory with the files from the ``syslinux`` directory using the following:
```
sudo cp /usr/lib/PXELINUX/pxelinux.0 /tftpboot
sudo cp /usr/lib/syslinux/modules/efi64/{libutil.c32,vesamenu.c32,menu.c32,libcom32.c32} /tftpboot
sudo cp /usr/lib/syslinux/modules/bios/ldlinux.c32 /tftpboot
```

Download your kernel and put it in the /tftpboot directory. It may be helpful to create a nested directory for this. For example, ShredOS is organized:
```yaml
/tftpboot/
  shredos/
    shredos # this is the kernel
  pxelinux.0
  ...
```

Then, create a place to store the PXELINUX config file:
```
sudo mkdir /tftpboot/pxelinux.cfg
sudo touch /tftpboot/pxelinux.cfg/default
```
Edit the ``default`` file with the location of the kernel and any appropriate kernel options. See the ShredOS example below.

If you are using ShredOS, [download the preconfigured PXELINUX environment](https://files.privex.io/images/iso/shredos/v1.1/pxeboot.tar.gz) and extract the files into the ``/tftpboot`` directory.

Edit ``pxelinux.cfg/default`` to read the following:
```yaml
#SERIAL 0 9600 0X008

# search path for the c32 support libraries (libcom32, libutil etc.)
path sys/

UI menu.c32

DEFAULT shredos

LABEL shredos
  KERNEL shredos/shredos
  #APPEND console=ttyS0,9600n8 simple quiet loglevel=0 console_baud=0
  # Fully automatic formatting of ALL DISKS
  APPEND console=tty0 autonuke method=zero rounds=1 nwipe_verify=last loglevel=0 console_baud=0

TIMEOUT 10
```

That is, comment out the ``SERIAL`` line and the first ``APPEND`` line. Then, uncomment the second ``APPEND`` line and remove ``simple`` from the kernel options. Finally, change ``console=console=ttyS0,9600n8`` to ``console=tty0``. 

> I found that the preconfigured environment is sometimes finicky. Check [the troubleshooting section](#troubleshooting-shredos-preconfigured-environment) for tips if you run into issues.

Now that all the tftp files are in place, configure the server by editing ``/etc/default/tftpd-hpa``:
```yaml
TFTP_USERNAME="tftp"
TFTP-DIRECTORY="/tftpboot"
TFTP_ADDRESS="192.168.0.105:69"
TFTP_OPTIONS="--secure"
```

Now, restart the tftpd-hpa service and test that it is working:
```
sudo systemctl restart tftpd-hpa.service
sudo systemctl status tftpd-hpa.service
```

### DHCP
The defaults file for ``isc-dhcp-server`` can be found in ``/etc/default/isc-dhcpd-server``. It should start looking like this:
```yaml
...
# On what interfaces should the DHCP server (dhcpd) serve DHCP requests?
#      Separate multiple interfaces with spaces, e.g. "eth0 eth1".
INTERFACESv4=""
INTERFACESv6=""
```

Edit the ``INTERFACESv4`` with the name of your interface:
```yaml
INTERFACESv4="eno1"
```

The config file can be found in ``/etc/dhcp/dhcpd.conf``. Edit it to contain this, replacing the addresses as necessary:
```yaml
subnet 192.168.0.0 netmask 255.255.255.0 {
  range 192.168.0.106 192.168.0.200;
  option routers 192.168.0.1;
  default-lease-time 3600;
  max-lease-time 86400;
  next-server 192.168.0.105;
  option bootfile-name "pxelinux.0";
  option tftp-server-name "192.168.0.105";
}

host desktop {
  hardware ethernet <your MAC address>;
  fixed-address 192.168.0.105;
}

ddns-update-style none;
authoritative;
```

At this point, the DHCP server should be all setup. Check that it is working with the following:
```
sudo systemctl restart isc-dhcp-server
sudo systemctl status isc-dhcp-server
```

### Boot to Network
If both the TFTP and DHCP servers are working, plug the server and any other client computers into a network switch and boot the client to the network.

### References
- (Youtube) [Setting up an UEFI PXE server on Linux (Part 1)](https://youtu.be/U3RC20ANomk)

---

## SLAX Linux
[**SLAX**](https://www.slax.org/) is a small and portable Linux operating system which runs from a USB without needing to be installed onto the hard drive, and it has built-in PXE boot capabilities. SLAX is preconfigured for PXE Booting other installations of SLAX over a network: [how PXE boot works in SLAX](https://www.slax.org/blog/20662-How-PXE-boot-works-in-Slax.html). However, this PXE Boot is only helpful if you want to use SLAX on the PXE clients. I manually setup a PXE server using the steps below.

### Setup
To start, install the necessary packages:
```
sudo apt-get -y update && sudo apt-get -y upgrade
sudo apt-get -y install dnsmasq tftpd-hpa pxelinux syslinux
```
``dnsmasq`` will act as the DHCP server, and ``tftpd-hpa`` will be the TFTP server. ``pxelinux`` and ``syslinux`` provide the necessary files and functionality for PXE booting.

Set a static IP by editing ``/etc/network/interfaces``:
```yaml
auto eno1
iface eno1 inet static
address 192.168.0.105
netmask 255.255.255.0
```

### TFTP
This TFTP server will be configured in the exact same way as the Ubuntu server. See [the TFTP section of the Ubuntu chapter](#tftp) for instructions.

### DHCP
To configure ``dnsmasq``, edit the config file found in:
```
sudo nano /etc/dnsmasq.conf
```
```yaml
dhcp-range=192.168.0.106,192.168.0.200,6h
dhcp-boot=pxelinux.0,192.168.0.105
interface=eno1
# dhcp-option 66 sets the "next-server", or the location of the tftp server
dhcp-option=66,"192.168.0.105"
```

Test that the dhcp server is working:
```
sudo systemctl restart dnsmasq
sudo systemctl status dnsmasq
```

### Boot to Network
If both the TFTP and DHCP servers are working, plug the server and any other client computers into a network switch and boot the client to the network.

---

## Troubleshooting and Workarounds
### Some NUC's cannot PXE boot ShredOS.
About half of the NUC's that I used came accross this issue:

1. **The NUC network boots like normal**. It is assigned an IP by the DHCP server and it retrieves the ShredOS kernel and associated files correctly. 
2. **ShredOS is automatically booted as normal**. As described above, the PXE boot menu appears as normal, and due to the ``TIMEOUT 10`` that was set, ShredOS is automatically loaded after 1 second.
3. **Instead of opening, an error log begins**. The system switches to ``runlevel: 0`` and shuts down.

Here is a recreation of the log:
```
Loading shredos/shredos... ok
INIT: version 2.88 booting
INIT: Entering runlevel: 3
Starting logging: OK
Starting thd: OK
Populating /dev using udev: done
Initializing random number generator... done.
Starting network: OK

INIT: Switching to runlevel: 0
INIT: Sending process the TERM signal
Stopping network: OK
Saving random seed... done
Stopping thd: OK
Stopping logging: OK
```

```
cat: can't open '/proc/cmdline': No such file or directory
cat: can't open '/proc/cmdline': No such file or directory
cat: can't open '/proc/cmdline': No such file or directory
cat: can't open '/proc/cmdline': No such file or directory
cat: can't open '/proc/cmdline': No such file or directory
cat: can't open '/proc/cmdline': No such file or directory
cat: can't open '/proc/cmdline': No such file or directory
cat: can't open '/proc/cmdline': No such file or directory
cat: can't open '/proc/cmdline': No such file or directory
getty: bad speed: console
cat: can't open '/proc/cmdline': No such file or directory
[repeated 12 times]
cat: can't open '/proc/cmdline': No such file or directory
getty: bad speed: console
INIT: Id "sole" respawning too fast: disabled for 5 minutes
```
The NUC's that do experience this issue look like they were all used for a single previous project, as they all have a similar label on the top of the case with the computer's name and its MAC address. Also, all of these NUC's have a 250 GB SSD as opposed to the 1 TB SSD's most of the other NUC's have. Other than this, I could not find any other differences.

#### ``can't open '/proc/cmdline': No such file or directory``
I found this forum post about a [similar issue with DBAN](https://sourceforge.net/p/dban/discussion/208932/thread/6bc10266/). I followed the steps some users posted about:

1. **Disable secure boot**. First I tried disabling secure boot and UEFI in the NUC's BIOS. To do so, I:
    - powered on the NUC,
    - tapped F2 to open the VisualBIOS,
    - navigated to "Advanced" and then to the "Boot" tab,
    - navigated to the "Secure Boot" tab within the Boot menu and ensured the "Secure Boot" option was unchecked.
    - Then, I navigated from the "Secure Boot" tab to "Boot Priority", and I unchecked the "UEFI Boot" option under the "UEFI Boot Priority" column.

&emsp;&emsp;&emsp;After following these steps, I was still unable to boot to ShredOS, as the same error still occurred.

2. **Append kernel parameters ``acpi=off nousb``**. I figured that since DBAN is the progenitor to ShredOS, these boot options might fix something. After network booting ShredOS, I made sure to hit the tab key to edit the boot options, adding these two parameters. Since some boot options were set in the ``pxelinux.cgf/default`` file already, the full options now read:
```
shredos/shredos console=tty0 autonuke method=zero rounds=1 nwipe_verify=last loglevel=0 console_baud=0 acpi=off nousb
```
&emsp;&emsp;&emsp;Despite this change, the same error message occurs. This time, however, the NUC doesn't shut off immediately, instead stalling on the last screen.


#### Workaround - Manually Boot ShredOS from USB
Since I was unable to find a way to get around this issue, I tested whether I could boot ShredOS from a bootable USB I had.

ShredOS installed and booted with no issues from the USB, and since it took about the same about of time to plug in the USB as it did to plug in a network cable, I decided just to boot any NUC's that didn't work with the network boot with the USB.

For reference, both the USB and the netboot image came from the same place: [Privex's ShredOS fork](https://githubmemory.com/repo/Privex/shredos). Specifically this [Bootable ShredOS ISO](https://files.privex.io/images/iso/shredos/v1.1/shredos.iso) and this [ShredOS Preconfigured PXE boot environment using PXELinux](https://files.privex.io/images/iso/shredos/v1.1/pxeboot.tar.gz).

### Troubleshooting TFTP Server - from Windows
You may want to make sure your TFTP server is working. I did so on my Windows laptop with the following steps:
1. Download the TFTP Client feature
    1. Open the Control Panel
    2. Navigate to Programs > Programs and Features > Turn Windows features on or off
    3. Check the box next to "TFTP Client", and click OK
2. Plug the computer into a network switch the server is connected to.
3. Use the Command Prompt to transfer a file:
    1. Open the Command Prompt
    2. Transfer ``menu.c32`` (or any other small file):
```
tftp 192.168.0.105 GET "menu.c32"
```
4. You should see something like the following confirming a file transfer:
```
Transfer successful: 27672 bytes in 1 second(s), 27672 bytes/s
```

### Troubleshooting TFTP Server - from the server
When trying to setup the TFTP server in SLAX, I found that sometimes the server would not start, giving me the following error when I checked the server status:
```
sudo systemctl status tftpd-hpa
```
```
... Control process exited, code=exited, status=71/OSERR
```

I also checked ``journalctl -xe`` and found the following error log:
```
... cannot bind to local IPv4 socket: Address already in use
```

I configured the TFTP server to run on port 69. So, I checked what was running on that port:
```
sudo netstat -lnp | grep 69
```
```
udp6    0     0   :::69         :::*            1254/xinetd
```

To resolve this, I stopped the xinetd service:
```
sudo systemctl stop xinetd
```

After restarting the ``tftpd-hpa`` service, this resolved the issue.


### Troubleshooting DHCP Server
You may also want to test your DHCP server. If you are connected to the DHCP server's network on a Windows computer, follow the steps below:
1. Open the Command Prompt
2. Type:
```
ipconfig /all | find /i “DHCP Server”
```
3. You should see the IP address of the server you setup. In my case it shows:
```
   DHCP Server . . . . . . . . . . . : 192.168.0.105
```

### Troubleshooting ShredOS Preconfigured Environment
The [preconfigured ShredOS PXELINUX environment](https://files.privex.io/images/iso/shredos/v1.1/pxeboot.tar.gz) directs the system to look in the ``tftpboot/sys/`` directory for the necessary booting files. However, sometimes this doesn't work. If the default setup for the environment isn't booting, try editing the ``/tftpboot/pxelinux.cfg/default`` file to read:

```yaml
# where to look for the GUI
UI menu.c32

DEFAULT shredos

# label in boot menu
LABEL ShredOS
  # relative location of kernel
  KERNEL shredos/shredos
  # append any kernel options
  APPEND console=tty0 autonuke method=zero rounds=1 nwipe_verify=last loglevel=0 console_baud=0

# tenths of a second to wait before autobooting
TIMEOUT 10
```

That is, remove the ``path sys/`` that was at the top of the file. Now, follow these steps to move the necessary files directly into the ``/tftpboot`` directory:
```
sudo cp /usr/lib/PXELINUX/pxelinux.0 /tftpboot
sudo cp /usr/lib/syslinux/modules/efi64/{libutil.c32,vesamenu.c32,menu.c32,libcom32.c32} /tftpboot
sudo cp /usr/lib/syslinux/modules/bios/ldlinux.c32 /tftpboot
```

At this point, the ``/tftpboot/sys/`` directory isn't used at all, so you could delete it. This step isn't necessary:
```
sudo rm -rf /tftpboot/sys/
```

Now try restarting the ``tftpd-hpa`` service and try again:
```
sudo systemctl restart tftpd-hpa.service
sudo systemctl status tftpd-hpa.service
```

---

## Running this server in the future
The NUC I used to setup the Ubuntu server has MAC Address 94-c6-91-a1-1f-a5

### Ubuntu
To start the same server I used again in the future, follow these instructions:
- Plug the NUC into a network switch.
- Boot the NUC to Ubuntu.
    - user: shredos
    - pass: shredos
- Type the following commands:
```
sudo systemctl restart isc-dhcp-server
sudo systemctl restart tftpd-hpa
```
- To ensure the DHCP and TFTP servers are running correctly, type: 
```
sudo systemctl status isc-dhcp-server
sudo systemctl status tftpd-hpa
```
- Plug another computer into the switch and boot it to the network.

### SLAX
To start the SLAX server:
- Plug the SLAX USB into a computer and plug the computer into a network switch.
- Boot the computer to SLAX.
- Start up the necessary services:
```
sudo systemctl restart dnsmasq
sudo systemctl restart tftpd-hpa
```
- Plug another computer into the switch and boot it to the network.

---

## Equipment and Other Notes
### Equipment
I had the following equipment available to use during this project:
- A [Dell Latitude 5590](https://www.dell.com/support/home/en-us/product-support/product/latitude-15-5590-laptop/docs) running Windows 10 Enterprise.
- 51 [Intel NUC's](https://ark.intel.com/content/www/us/en/ark/products/95067/intel-nuc-kit-nuc7i5bnh.html).
  - These had varying specs. About half had a 1 TB SSD, and the other half had a 250 GB SSD.
- A 24-port [Netgear ProSafe Plus JGS524E](https://www.netgear.com/support/product/JGS524E.aspx) Network Switch.

### Possibly Useful Information
Below is some information I learned over the course of the project, which may be helpful to someone who doesn't know much terminology.

#### 1. PXE
- **PXE** (commonly pronounced "*pixie*", or used in the phrase "*PXE boot*"), [_Preboot eXecution Environment_](https://en.wikipedia.org/wiki/Preboot_Execution_Environment), is a specification describing a standardized environment that allows PXE-enabled client computers to boot a specific operating system or other software (configured and distributed by a server) over a network.
- Since PXE is a widely adopted standard, most computers can be PXE-enabled through their BIOS or are already PXE-enabled.
- In practice, setting up a PXE boot server entails configuring a **DHCP** server and a **TFTP** or other file transfer system server (see below).

#### 2. DHCP
- **DHCP** is an acronym for [_Dynamic Host Configuration Protocol_](https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol). It is a protocol for dynamically and automatically assigning and managing IP addresses within a network. 
- When a DHCP server is setup, a pool of IP addresses is specified for the server to pick from. Each time a client joins the network, it is dynamically assigned an IP address by the server, and when it leaves that address is reclaimed.
- By assigning an IP address to each computer on the network, a DHCP server allows for computers on the network to communicate.

#### 3. TFTP
- **TFTP**, or [_Trivial File Transfer Protocol_](https://en.wikipedia.org/wiki/Trivial_File_Transfer_Protocol), allows client computers to get a file from or put a file on a server.
- TFTP servers are commonly used for PXE booting since they are simple to setup.

In this way, a PXE boot server needs:
1. a way for the client computers to communicate with the server (DHCP),
2. a method of transferring files from the server to the client (TFTP), and
3. the set of instructions for the client to follow (the bootloader and kernel).

### Links
Here are links that may be helpful if attempting a different implementation of a PXE server:
- [iPXE](https://ipxe.org/)
  - An open source network boot firmware. I instead ended up using [PXELINUX](https://wiki.syslinux.org/wiki/index.php?title=PXELINUX) instead.
- [netboot.xyz](https://netboot.xyz/docs/faq/)
  - A removable-media-bootable utility that uses iPXE to allow for PXE booting of multiple operating systems.
- [ShredOS](https://github.com/PartialVolume/shredos.x86_64)
  - A Linux operating system and descendant of [DBAN](https://dban.org/) designed for the sole purpose of securely erasing the entire contents of a disk using [nwipe](https://github.com/martijnvanbrummelen/nwipe).
- [Privex ShredOS Fork](https://githubmemory.com/repo/Privex/shredos#kernel-boot-flags)
  - This is a fork of ShredOS which is managed by [Privex](https://www.privex.io/). This fork contains some pre-built ShredOS images, including a USB-bootable version as well as a PXE boot environment using [PXELINUX](https://wiki.syslinux.org/wiki/index.php?title=PXELINUX)