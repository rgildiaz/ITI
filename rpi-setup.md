# Configure and Clone Raspberry Pi

This document will walk through the process I followed to configure and clone the Raspberry Pi 3B+'s used for the Liberty Eclipse training program project. These Pi's were used for data collection purposes during the setup for the program, and they will be used during the program for management and collection purposes as well.

#### Contents:
- [Raspberry Pi Setup](#raspberry-pi-setup)
- [Clone Using WinDiskImager and Rufus](#clone-using-win32diskimager-and-rufus)
- [Post-Image Configuration](#post-image-configuration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Equipment & Other Notes](#equipment--other-notes)

---

## Raspberry Pi Setup
The first step in this process is setting up a single Pi to use as the base image. To do so, we will need to install an operating system, install any additional software that will be needed on every machine, and then change any settings that will apply to every machine.

Note that during this process, you will need some way to connect a microSD card to a computer running Windows.

### Install Raspberry Pi OS Lite (32-bit)
Raspberry Pi provides the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on their site, which is a utility that can be used to install Raspberry Pi OS on the Pi that will be used as the image. The Imager is available on Windows, MacOS, and Ubuntu.

To start, download the imager and launch it. You should see a screen with the Raspberry Pi logo and three buttons: ``CHOOSE OS``, ``CHOOSE STORAGE``, and ``WRITE``. Click ``CHOOSE OS``, then the second option for ``Raspberry Pi OS (other)``, and then ``Raspberry Pi OS Lite (32-bit)``. 

Now that the correct OS has been chosen, click the ``CHOOSE STORAGE`` button. Connect the microSD card to your computer (using an adapter or otherwise), and it should appear in the list of drives in the ``STORAGE`` window. Select it, and then click ``WRITE`` to begin the process of writing the operating system to the SD card.

### VLAN Setup
Install the VLAN package with: 
```
sudo apt install vlan
```



## Clone Using Win32DiskImager and Rufus
### Image with Win32DiskImager
[Win32DiskImager](https://win32diskimager.org/) is a free software utility for Windows. It can be used both to create images from disks as well as to write images to disks. In this case, I only used it to create an image of the Raspberry Pi I originally configured, and I used Rufus to write the image to the SD cards of the other Pi's (since Rufus is marginally faster and lighter-weight).

If you are not using Windows, you can also create an image using the ``dd`` disk utility tool in Linux or any alternative software for MacOS.

To begin, power off the Pi you are imaging and remove the microSD card. The laptop I am using has a built-in SD card reader, so I can use a microSD to SD card adapter, but you may need to use a USB extension or adapter to connect the microSD card to your laptop.

### Write with Rufus
[Rufus](https://rufus.ie/en/) is a software utility for Windows 7 or later which can be used to format and create bootable removable media drives. It is very small, relatively fast, and free to use.

## Post-Image Configuration

## Deployment

## Troubleshooting
### Clonezilla
When deciding how to clone the first Raspberry Pi I setup, I first attempted to use [Clonezilla](https://clonezilla.org/), a popular disk cloning tool which is USB-bootable and can easily be used in conjunction with a PXE server for mass deployment. While I was able to make a direct image of the Pi I used, it might have been more convenient to make a Clonezilla image. However, I ran into some trouble, detailed below.

I used version 3.0.1-8-amd64. To download it for yourself, visit [the Clonezilla download page](https://clonezilla.org/downloads/download.php?branch=stable), select the correct architecture, change the file type to iso, set the repository to auto, and then click ``Download``. Once the ISO is downloaded, you can use [Rufus](https://rufus.ie/en/) following [the same method outlined above](#write-with-rufus) to write Clonezilla to a USB stick.

## Equipment & Other Notes
Included below is a list of equipment used during this process as well as the version numbers of software used.

Hardware:
- 20 [Raspberry Pi 3B+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/)'s, each installed with a [PoE+ HAT](https://www.raspberrypi.com/products/poe-plus-hat/)
- a [Dell Latitude 5590](https://www.dell.com/support/home/en-us/product-support/product/latitude-15-5590-laptop/overview) Laptop running [Windows 10 Enterprise, Version 21H2](https://docs.microsoft.com/en-us/windows/release-health/status-windows-10-21h2) and [Ubuntu Server 22.04.1](https://ubuntu.com/download/server)

Software:
- 