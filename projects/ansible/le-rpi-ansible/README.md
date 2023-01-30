# Verify LE Raspberry Pi's with Ansible

Ansible script to verify the Raspberry Pi's used for Liberty Eclipse 2022.

See [what I wrote for this public repository](./verify-w-ansible.md) for information about my methodology.

## Scope
This script will:
- check that all packages specified in ``vars/packages.txt`` are installed,
- verify that NTP is configured,
- check that an ``rsync-pcap.sh`` script has been installed, and
- use the [default configuration specified below](#defaults).

## Usage
```bash
$ ansible-playbook rpi-installs.yml
```

## Configuration
### Login/Connection
By default, the script will check for all the hosts in the ``le-rpi-hosts`` file within the ``[remote]`` group. You can edit this with any extra hosts.

Settings for ansible groups are stored in the ``grouped_vars`` dir. By default, the ``[remote]`` group will connect with ssh.

SSH private key location is specified in ``ansible.cfg``, and by default this is ``~/.ssh/le22_rpi_manager.priv``. Edit the ``private_key_file`` entry in this ``.cfg`` file to change where Ansible will look for the key.

This script is setup to connect as the user account ``manager``. This is specified with the ``remote_user`` attribute found at the top of ``rpi-installs.yml``. 

### Packages
The script will check for all packages listed in ``vars/packages.txt``. Add new packages on a new line, and specify package version with ``foo=1.1.1``. 

Some packages not installed using ``apt`` are not detected by Ansible's builtin package manager. These can be checked by adding tasks to the ``tasks/manual_package_tasks.yml`` file.

### NTP
This script will check for the line ``NTP=10.4.0.101 10.4.0.102`` within the ``/etc/systemd/timesyncd.conf`` file. For different NTP servers, edit this line in ``rpi-installs.yml``.

By default, this script checks that the ``systemd-timesyncd`` service is running using the ``ansible.builtin.service_facts`` plugin.

### Rsync
Rsync is verified by ensuring that ``/etc/scripts/rsync-pcap.sh`` exists. I chose not to verify the contents of the script since it may be changed in the future.

The super user permissions granted by ``become: yes`` at the top of ``rpi-installs.yml`` are necessary to access the cronjob file at ``/var/spool/cron/crontabs/root``, which is how the ``cronjob`` configuration is verified.

## Defaults
### Login
- via ``ssh`` as the user ``manager`` using a private key located at ``~/.ssh/le22_rpi_manager.priv``.
- super user privileges granted via ``become: yes``.
    - this is used for [rsync](#rsync).

### Hosts
```
10.4.0.103
10.4.0.105
10.4.0.106
10.4.0.107
10.4.0.108
10.4.0.109
10.4.0.119
10.4.0.111
10.4.0.112
10.4.0.121
10.4.0.122
10.4.0.139
10.4.0.130
10.4.0.131
10.4.0.132
10.4.0.134
```

### Packages
```
./vars/packages.txt
│   vlan
│   autossh
│   tcpdump
│   rsync
│   picocom
│   telegraf
│   vim
│   tshark
│   pip

./tasks/manual_package_tasks.yml
│   rflowman
│   ryu=4.34
```
