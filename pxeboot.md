# PXE Boot ShredOS

This document will walk through the process I used to wipe 50 Intel NUC's by setting up a PXE server to network boot ShredOS. I will cover the different methods and tools I tried for setting up a PXE server, including Windows ADK and SLAX, as well as how I eventually successfully configured a PXE server in [Ubuntu Server 20.04.4 LTS](https://releases.ubuntu.com/20.04/). The last section will cover troubleshooting and workarounds I needed to use in some cases.

The sections "Ubuntu Server" and "SLAX Linux" each describe the working servers in each of those operating systems.

#### Contents:
- [Ubuntu Server 20.04.4](#ubuntu-server-20044)
- [SLAX Linux](#slax-linux)
- [Troubleshooting and Workarounds](#troubleshooting-and-workarounds)
- [Equipment and Other Notes](#equipment-and-other-notes)

---

## Ubuntu Server 20.04.4
Around this time, Matthew also gave me a USB installer for [Ubuntu Server 20.04.4](https://releases.ubuntu.com/20.04/). While I first tried to setup a new PXE server in SLAX, I realized that I would be able to find much more Ubuntu-specific information and tutorials, so I installed Ubuntu on a NUC and switched over.

---

## SLAX Linux
### SLAX
After asking Matthew for some more help getting started, he gave me a bootable USB with [SLAX](https://www.slax.org/) Linux on it. 

[**SLAX**](https://www.slax.org/) is a small and portable Linux operating system which runs from a USB without needing to be installed onto the hard drive, and it has built-in PXE boot capabilities. Matthew also sent me this blog post about [how PXE boot works in SLAX](https://www.slax.org/blog/20662-How-PXE-boot-works-in-Slax.html).

I plugged the USB into a NUC, and I was able to start a PXE server just using the command:

    /sbin/pxe

After short trial and error, I got SLAX booted on a PXE client computer just by plugging both the client and the server into the network switch and booting the client from the network.

I spent some time attempting to figure out a way to boot other operating systems from the SLAX PXE server, but I couldn't find or understand what I would need to change. There is some mention of the files that are created and loaded by SLAX when using it as a PXE server in the blog post I linked above about [PXE boot in SLAX](https://www.slax.org/blog/20662-How-PXE-boot-works-in-Slax.html), but since I didn't know much about what each file does, I didn't know what to change within SLAX.

In the comments of this blog post thread, I found mention of ``pxelinux.0`` files. After researching [PXELINUX](https://wiki.syslinux.org/wiki/index.php?title=PXELINUX) (below) I thought it might make more sense to setup a PXE server using PXELINUX from scratch rather than trying to dig into the files I didn't understand within SLAX.

Around this time, Matthew sent me this article about how somebody setup a [PXE server for DBAN](https://www.nang.io/pxe-boot-dban/). While DBAN is no longer maintained, I might be able to follow these steps to setup a PXE server for ShredOS.

I won't go into too much detail about this since I never got this working, but there are some things that I now understand that I did incorrectly:
- The tutorial instructs to add this to the bottom of the ``etc/network/interfaces`` file:
```
auto eth1
iface eth1 inet static
address 10.0.0.1
netmask 255.255.255.0
```
&emsp;&emsp;&emsp;I added it verbatim, but I should have checked my ethernet name using something like ``ip a``. The ``ip a`` command shows that in this version of Linux, the interface name is ``eno1`` not ``eth1``.

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

[There is more text between these two screens, but I was unable to read it or screenshot it before it moves away.]

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

#### runlevels
While researching this issue, I found this article about [runlevels in Linux](https://tldp.org/LDP/sag/html/run-levels-intro.html), which shed a small amount of light on what was going on. While booting, the system attempts to boot as normal in ``runlevel: 3``, which indicates Full Multiuser with Networking access. This is necessary since the client needs access to Networking tools like TFTP. However, it is signaled to ``switch to runlevel: 0``, which signals to halt the system. Everything is shut down, and the computer exits.

#### ``can't open '/proc/cmdline': No such file or directory``
I found this forum post about a [similar issue with DBAN](https://sourceforge.net/p/dban/discussion/208932/thread/6bc10266/). I followed the steps some users posted about:

1. **Disable secure boot**. First I tried disabling secure boot and UEFI in the NUC's BIOS. To do so, I:
  - powered on the NUC,
  - tapped F2 to open the VisualBIOS,
  - navigated to "Advanced" and then to the "Boot" tab,
  - navigated to the "Secure Boot" tab within the Boot menu and ensured the "Secure Boot" option was unchecked.
  - Then, I navigated from the "Secure Boot" tab to "Boot Priority", and I unchecked the "UEFI Boot" option under the "UEFI Boot Priority" column.

&emsp;&emsp;&emsp;After following these steps, I was still unable to 
boot to ShredOS, as the same error still occurred.

2. **Append kernel parameters ``acpi=off nousb``**. I figured that since DBAN is the progenitor to ShredOS, these boot options might fix something. After network booting ShredOS, I made sure to hit the tab key to edit the boot options, adding these two parameters. Since some boot options were set in the ``pxelinux.cgf/default`` file already, the full options now read:
```
shredos/shredos console=tty0 autonuke method=zero rounds=1 nwipe_verify=last loglevel=0 console_baud=0 acpi=off nousb
```
&emsp;&emsp;&emsp;Despite this change, the same error message occurs. This time, however, the NUC doesn't shut off immediately, instead stalling on the last screen.


#### Workaround - Manually Boot ShredOS from USB
Since I was unable to find a way to get around this issue, I tested whether I could boot ShredOS from a bootable USB I had.

ShredOS installed and booted with no issues from the USB, and since it took about the same about of time to plug in the USB as it did to plug in a network cable, I decided just to boot any NUC's that didn't work with the network boot with the USB.

For reference, both the USB and the netboot image came from the same place: [Privex's ShredOS fork](https://githubmemory.com/repo/Privex/shredos). Specifically this [Bootable ShredOS ISO](https://files.privex.io/images/iso/shredos/v1.1/shredos.iso) and this [ShredOS Preconfigured PXE boot environment using PXELinux](https://files.privex.io/images/iso/shredos/v1.1/pxeboot.tar.gz).

---

## Conclusion: Running this server in the future
The NUC I used to setup this server has MAC Address 94-c6-91-a1-1f-a5

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

---

## Equipment and Other Notes
### Equipment
I had the following equipment available to use during this project:
- A [Dell Latitude 5590](https://www.dell.com/support/home/en-us/product-support/product/latitude-15-5590-laptop/docs) running Windows 10 Enterprise.
- 51 [Intel NUC's](https://ark.intel.com/content/www/us/en/ark/products/95067/intel-nuc-kit-nuc7i5bnh.html).
  - These had varying specs. About half had a 1 TB SSD, and the other half had a 250 GB SSD.
- A 24-port [Netgear ProSafe Plus JGS524E](https://www.netgear.com/support/product/JGS524E.aspx) Network Switch.

### Initial Research
While I wasn't sure where to start when beginning this project, I was given an initial direction: find a way to setup a PXE boot server which I could use to deploy ShredOS, connect it to a network switch, and then connect the other NUC's to the switch to erase their drives automatically.

Below are some initial links I referenced (provided by Matthew):

- [iPXE](https://ipxe.org/)
  - An open source network boot firmware. I instead ended up using [PXELINUX](https://wiki.syslinux.org/wiki/index.php?title=PXELINUX) instead (see section 2).
- [netboot.xyz](https://netboot.xyz/docs/faq/)
  - A removable-media-bootable utility that uses iPXE to allow for PXE booting of multiple operating systems.
- [ShredOS](https://github.com/PartialVolume/shredos.x86_64)
  - A Linux operating system and descendant of [DBAN
  ](https://dban.org/) designed for the sole purpose of securely erasing the entire contents of a disk using [nwipe](https://github.com/martijnvanbrummelen/nwipe).
- [Privex ShredOS Fork](https://githubmemory.com/repo/Privex/shredos#kernel-boot-flags)
  - This is a fork of ShredOS which is managed by [Privex](https://www.privex.io/). This fork contains some pre-built ShredOS images, including a USB-bootable version as well as a PXE boot environment using [PXELINUX](https://wiki.syslinux.org/wiki/index.php?title=PXELINUX)

Lacking prior knowledge of many of the topics discussed throughout these articles, here is the fundamental information I gleaned from initial research:

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
