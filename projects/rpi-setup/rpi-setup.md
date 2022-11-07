# Configure and Clone Raspberry Pi

This document will walk through the process I followed to configure and clone the Raspberry Pi 3B+'s used for the Liberty Eclipse project.

#### Contents:
- [Raspberry Pi Setup](#raspberry-pi-setup)
- [Clone Using Win32DiskImager and Rufus](#clone-using-win32diskimager-and-rufus)
- [Post-Image Configuration](#post-image-configuration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Equipment & Other Notes](#equipment--other-notes)

---

## Raspberry Pi Setup
The first step in this process is setting up a single Pi to use as the base image. To do so, it will need to:
1. have an operating system installed,
2. have any additional software installed, and
3. have any configuration or setting changes that will apply to every machine installed.

Note that if you are following the same process I did, you will need some way to connect a microSD card to a computer running Windows.

### Install PoE HAT
Before beginning the process of installing Raspberry Pi OS and other software onto each Pi, I first installed a [PoE HAT](https://www.raspberrypi.com/products/poe-hat/) on each device.A HAT is an expansion card that sits on top of each Pi for added functionality. This HAT's only purpose is to add PoE functionality. 

The installation process is very straightforward and can be completed only with a small Phillips-head screwdriver. 

Once the PoE HAT is installed, move on to the next step.

### Install Raspberry Pi OS Lite (32-bit)
Raspberry Pi provides the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on their site. This is a utility that can be used to install Raspberry Pi OS on the device that will be configured and imaged. The Raspberry Pi Imager is available on Windows, MacOS, and Ubuntu.

To start, download the Imager and launch it. Once it launches, the application window should show the Raspberry Pi logo and three buttons: "CHOOSE OS", "CHOOSE STORAGE", and "WRITE". The "WRITE" button should be grayed out for now. Click "CHOOSE OS", then in the window that appears choose the second option for "Raspberry Pi OS (other)", and finally "Raspberry Pi OS Lite (32-bit)". 

Now that the correct OS has been chosen, click the "CHOOSE STORAGE" button. A few seconds after connecting the microSD card to the computer (using an adapter or otherwise), it should appear in the list of drives in the "STORAGE" window. Select it, and then click "WRITE" to begin the process of writing the operating system to the SD card.

In my experience, it can take anywhere from 5 to 15 minutes for the operating system to be written to the card.

Once it's been written, eject the microSD card from your SD card reader and plug it back into the Raspberry Pi. Supply power to the Pi by connecting it to either a PoE enabled ethernet port or using the microUSB power cable that it came with.

The Pi should boot after a few seconds to the setup screen. Proceed through this process to configure the Pi as desired, and then reboot it to finish the setup process.

Once the Pi boots, continue to the next step.

### Software Installation
Now that the Pi has its initial configuration, it can be installed with the various software packages needed. I've included below a list of the software and versions needed for this project:
- ``vlan``
- ``tcpdump``
- ``autossh``
- ``picocom``
- ``telegraf``
    - ``telegraf`` has a [special installation process detailed on their website](https://github.com/influxdata/telegraf).
- ``vim``
- ``tshark``
- ``pip3``
- ``ryu``
    - ``ryu`` needs to be installed via pip, as it isn't available through ``apt``.
- ``rflowman``
  - ``rflowman`` is not available through ``apt``. Use the binary located at ``resources/rflowman``

Since we will need all these packages, everything that is available through ``apt`` can be installed at once:
```bash
sudo apt-get -y update && sudo apt-get -y upgrade
sudo apt install vlan tcpdump autossh picocom vim tshark pip3
```

At this point, ``ryu`` and ``telegraf`` should be the only packages left needed to be installed.

To install ``telegraf``, the Pi first needs to add the repository key and setup a new ``sources.list`` entry:
```bash
# influxdb.key GPG Fingerprint: 05CE15085FC09D18E99EFB22684A14CF2582E0C5
wget -q https://repos.influxdata.com/influxdb.key
echo '23a1c8836f0afc5ed24e0486339d7cc8f6790b83886c4c96995b88a061c5bb5d influxdb.key' | sha256sum -c && cat influxdb.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdb.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdb.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
sudo apt-get update && sudo apt-get install telegraf
```
> see the instructions on the [``telegraf`` GitHub page](https://github.com/influxdata/telegraf#package-repository) for more information.

To install ``ryu``, use ``pip3``:
```bash
pip3 install ryu
pip3 install --upgrade six
```
> Note that ``ryu`` is currently unmaintained, which caused us issues during this process. See the [``ryu`` GitHub page](https://github.com/faucetsdn/ryu) for more information.

#### VLAN Setup
Since the ``vlan`` package was just installed, it now needs to be configured. The first step is editing the ``/etc/modules`` file:
```bash
echo 8021q >> /etc/modules
```

Then, reboot the Pi. To tag an interface, edit the ``/etc/network/interfaces.d/vlans`` file:
```bash
sudo nano /etc/network/interfaces.d/vlans
```

For each entry, add:
```yaml
auto <interfacename>.<vlannum>
iface <interfacename>.<vlannum> inet manual
  vlan-raw-device <interfacename>
```

For example, all the Pi's will have an ``eth1`` interface with a VID of 902:
```yaml
auto eth1.902
iface eth1.902 inet manual
  vlan-raw-device eth1
```

Finally, add the interface config to ``/etc/dhcpcd.conf``:
```yaml
# A sample configuration for dhcpcd
...
# Example static IP configuration:
interface eth1
static ip_address=10.4.0.112/23
#static ip6_address=
static routers=10.4.0.1
static domain_name_servers=10.4.0.2

# --- LINES BELOW ADDED ---
interface eth1.902
static ip_address=10.4.4.112/24
```

For the changes to take effect, either restart networking services or restart the Pi:
```bash
sudo systemctl restart networking
```

In our case, see [the list of Pi hostnames and IP's used here](resources/rpi-list.txt) for information on how each Pi should be configured.
> Since the hostnames and non-.902 interfaces are different for each Pi, I set these during the [post-imaging configuration](#post-image-configuration).

### Edit Common Settings and Configurations
#### IP
All the Pi's were configured such that the ``eth0`` interface can be used solely for ``tcpdump`` collection rather than network connectivity. Edit ``/etc/network/interfaces`` to be the following:
```ini
auto lo
iface lo inet loopback

autp eth0
iface eth0 inet manual
```

#### NTP Time Setup
All Pi's were also configured with the same NTP settings. This can be configured in ``timesyncd.conf``:
```bash
sudo nano /etc/systemd/timesyncd.conf
```
Edit the file as follows:
```ini
...
[Time]
NTP=10.4.0.101 10.4.0.102
# FallbackNTP=
RootDistanceMaxSec=5
PollIntervalMinSec=32
PollIntervalMaxSec=2048
```

For the changes to take effect, run the following:
```bash
sudo timedatectl set-ntp true
sudo systemctl restart systemd-timesyncd.service
```

#### Root and User Password
All the Pi's need the same root and user passwords. In this case, I named the user account ``manager``.
```bash
sudo passwd root
New password:
```

```bash
sudo passwd manager
New password:
```

#### Add Scripts
David provided multiple scripts to be added to the Pi's. You can find all of them in the ``resources/scripts`` directory. Some of these will be stored in a new directory, ``/etc/scripts``. At the same time, create a directory specifically for rflowman scripts:
```bash
sudo mkdir /etc/scripts
sudo mkdir /etc/scripts/rflowman
```

Now that these are in place, the files can be transferred to the Pi. The easiest way for me to do so was via a USB stick.

Plug the USB into the non-Pi computer and transfer the files from ``resources/scripts`` to it. Eject the USB and transfer it to the Pi. Mount it and copy the files to the appropriate directory:
```bash
# find the device and partition name with lsblk
sudo lsblk
sudo mount /dev/sda1 /media/usb
sudo cp /media/usb/rsync-pcap.sh /etc/scripts
sudo cp /media/usb/exercise_flows.json /etc/scripts/rflowman
# the .service files go in /usr/lib/systemd/system
sudo cp /media/usb/{capture.service,rflowman.service,ryu-manager.service} /usr/lib/systemd/system
```

Once the scripts are in place, setup a root ``cron`` job to run the ``rsync-pcap.sh`` script every 15 minutes:
```bash
sudo crontab -e
```
```ini
# Edit this file to introduce tasks to be run by cron.
...
# m h dom mon dow   command
*/15 * * * * /etc/scripts/rsync-pcap.sh
```

### Closing
Now that this basic Pi is setup as much as possible (before doing anything device-specific), it is ready to be imaged and distributed to the other devices.

## Clone Using Win32DiskImager and Rufus
### Image with Win32DiskImager
[Win32DiskImager](https://win32diskimager.org/) is a free software utility for Windows. It can be used both to create images from disks as well as to write images to disks. In this case, I only used it to create an image of the Raspberry Pi I originally configured, and I used Rufus to write the image to the SD cards of the other Pi's (since Rufus is marginally faster and lighter-weight).

If you are not using Windows, you can also create an image using the ``dd`` disk utility tool in Linux or any alternative software for MacOS.

To begin, power off the Pi you are imaging and remove the microSD card. The laptop I am using has a built-in SD card reader, so I can use a microSD to SD card adapter, but you may need to use a USB extension or adapter to connect the microSD card to your laptop.

### Write with Rufus
[Rufus](https://rufus.ie/en/) is a software utility for Windows 7 or later which can be used to format and create bootable removable media drives. It is very small, relatively fast, and free to use. Now that an image of a Pi is saved to the computer, we can use Rufus to write it to a new microSD card.

Plug a new microSD (not the one used for the original Pi) into the computer and launch Rufus. In the "Device" dropdown at the top of the Rufus window, you should see your SD card reader. Select it. 

In the "Boot Selection" dropdown, choose "Disk or ISO image". Then, click the "SELECT" button to the right of that menu. Navigate to the image that was saved to your computer and select it.

Finally, click the "START" button at the bottom of the window to begin the process of writing the image to the microSD card. You can expect this process to take around 15 minutes if you used a 64 GB microSD card in the original Pi.

Once the image has been written, you can eject the SD card and plug it into a new Raspberry Pi. It should boot up and look the exact same as the original Pi that was imaged.

## Post-Image Configuration
After each Pi is cloned and working with the original image, some further configuration has to be done. 

### Set Hostname
Each Pi is assigned a different hostname. To edit this, edit the following files:
```
sudo nano /etc/hostname
```

```
sudo nano /etc/hosts
```

### Configure VLAN and IP
Each Pi is also assigned a different IP address (given by David, see [the list of hostnames and IP's](resources/rpi-list.txt)), as well as different VLAN IP's and tags.
```
sudo nano /etc/network/interfaces.d/vlans
```
```
sudo nano /etc/dhcpcd.conf
```

### Mount USB
Each Pi also needs a USB mounted to the ``/mnt`` directory for log storage. To start, create a subdirectory to store the data in:
```
sudo mkdir /mnt/external
```

Then, insert and mount the USB:
```bash
# find the partition name
sudo fdisk -l
sudo mount /dev/sda1 /mnt/external
```

Finally, create subdirectories of ``external``:
```
sudo mkdir /mnt/external/{pcaps,data}
sudo mkdir /mnt/external/pcaps/pcaps
```

## Troubleshooting
### Clonezilla
When deciding how to clone the first Raspberry Pi I setup, I first attempted to use [Clonezilla](https://clonezilla.org/), a popular disk cloning tool which is USB-bootable and can easily be used in conjunction with a PXE server for mass deployment. While I was able to make a direct image of the Pi I used, it might have been more convenient to make a Clonezilla image. However, I ran into some trouble, detailed below.

I used version 3.0.1-8-amd64. To download it for yourself, visit [the Clonezilla download page](https://clonezilla.org/downloads/download.php?branch=stable), select the correct architecture, change the file type to iso, set the repository to auto, and then click ``Download``. Once the ISO is downloaded, you can use [Rufus](https://rufus.ie/en/) following [the same method outlined above](#write-with-rufus) to write Clonezilla to a USB stick.

## Equipment & Other Notes
Included below is a list of equipment used and software versions.

### Hardware:
- 20 [Raspberry Pi 3B+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/)'s, each installed with a [PoE HAT](https://www.raspberrypi.com/products/poe-hat/)
- a [Dell Latitude 5590](https://www.dell.com/support/home/en-us/product-support/product/latitude-15-5590-laptop/overview) Laptop running [Windows 10 Enterprise, Version 21H2](https://docs.microsoft.com/en-us/windows/release-health/status-windows-10-21h2) and [Ubuntu Server 22.04.1](https://ubuntu.com/download/server)

### Software:
Name        | Version
------------|-----------
``vlan``    | 2.0.5
``tcpdump`` | 4.99.0
``autossh`` | 1.4
``picocom`` | 3.1
``telegraf``| 1.23.4
``vim``     | 8.2.2434
``tshark``  | 3.4.10
``pip3``    | 20.3.4
``ryu``     | 4.34
``rflowman``| 7.0.0