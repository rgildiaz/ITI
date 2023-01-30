# Verify Installations Remotely with Ansible

For this project, my supervisor gave me the opportunity to write an [Ansible](https://www.ansible.com/) script to verify the installations of several [Raspberry Pis](https://www.raspberrypi.com/), which I initially setup earlier this year for the Liberty Eclipse project (see [my documentation about the process](../rpi-setup/rpi-setup.md)).

You can find the documentation I wrote for this project in [this directory's README.md](./README.md). Included in this directory are all the resources I used to get this working over a remote VPN connection _``except the private ssh key :^)``_. 

## Contents
- [Ansible](#ansible)
- [Methodology](#methodology)
    - [Background and Configuration](#background-and-configuration)
    - [The Playbook](#the-playbook)
- [For more information...](#for-more-information)

## Ansible
Ansible is an automation technology built on Python and managed by [Red Hat](https://www.redhat.com/en) which is commonly used for IT operations work. Before beginning this project, I had no exposure to Ansible, but its [simple syntax](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html) and [extensive documentation](https://docs.ansible.com/ansible/latest/index.html) made it relatively easy to learn.

While I did complete a couple LinkedIn Learning courses about Ansible ([course 1](https://www.linkedin.com/learning/learning-ansible-2020) and [course 2](https://www.linkedin.com/learning/ansible-essential-training-14199798)), I found that running into problems and finding solutions on my own was both much more productive and much more engaging.

## Methodology
When I was tasked with writing this script, my manager let me know that **no changes should be made to any of the devices on which the script is run.** This informed many of my decisions.

### Background and Configuration
Ansible scripts take the format of [playbooks](https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html), in which series of tasks can be specified. The main playbook for this program is [``rpi-installs.yml``](./rpi-installs.yml). To run this playbook, the following command could be executed:
```bash
$ ansible-playbook rpi-installs.yml
```

When a playbook is run, Ansible checks for an [``ansible.cfg``](./ansible.cfg) file in the working directory. In here, you can see that I specify paths to important files:
```ini
inventory = le-rpi-hosts
private_key_file = ~/.ssh/le22_rpi_manager.priv
```

[The inventory](./le-rpi-hosts) contains a list of all hosts to be operated on. 

The private key file is used by Ansible in order to remotely connect via ssh.

Ansible also checks the ``grouped_vars`` directory when running a playbook. Here I have the [``remote.yml``](./grouped_vars/remote.yml) file, which contains variable which are applied to the ``[remote]`` group.

At the top of ``rpi-installs.yml``, you should see:
```yml
hosts: remote
remote_user: manager
become: yes
```

``hosts: remote`` asks Ansible to use the ``[remote]`` group, specified in the inventory file (which was gathered earlier from ``ansible.cfg``). ``remote_user: manager`` and ``become: yes`` ask Ansible to connect to each host as the user ``manager`` and to attempt to ``become`` a super user (this is important for some of the later tasks).

### The Playbook
In [``rpi-installs.yml``](./rpi-installs.yml), the ``tasks:`` block contains all the actions that Ansible takes on host systems.

The main goals of this playbook are to:
1. Make sure all the necessary packages are installed,
2. Verify that an NTP time server is setup, and
3. Ensure an rsync script is in place and running.

I've organized these goals into blocks, so I'll go through them one-by-one.

#### Check package installs
When designing this section of the script, I wanted it to be easy to maintain and manage. The solution I landed on involves pulling a list of packages from an external file ([``vars/packages.txt``](./vars/packages.txt)).

First, we need a way to allow Ansible to check what packages are installed on host systems. The builtin Ansible [``package``](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/package_module.html) module allows for this functionality, and the first task in this block sets this up and gathers the necessary facts.

Next, to store a list of packages which are not installed (which will later be printed), Ansible stores an empty list in a global variable called ``not_found_packages``.

To iterate over the packages which are listed in [``vars/packages.txt``](./vars/packages.txt), Ansible provides a builtin [loop](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/items_lookup.html) functionality. For this to work cleanly, I used the [``include_tasks``](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/include_tasks_module.html) module, which allows for the execution of tasks which are stored outside the current playbook. In this case, Ansible first pulls the list of packages from ``vars/packages.txt`` before performing the tasks specified at [``tasks/package-tasks.yml``](tasks/package_tasks.yml) for each item.

``package-tasks.yml`` fails if it can't find the package it is given. The failure is caught by the ``rescue: `` block, which adds it to the list of missing packages before the loop continues to the next item.

There are some items which cannot be checked with the ``package`` module. To avoid bloat in the main playbook, tasks which manually check for these are stored in [``tasks/manual_package_tasks.yml``](tasks/manual_package_tasks.yml).

In this version of the program, the only packages which need to be checked for manually are ``ryu`` and ``rflowman``. To do this, Ansible executes the package with the ``--version`` option or the ``version`` parameter and checks the stdout against a predefined value.

Once all the packages have been checked, Ansible prints the list of those which were not found.

#### Check NTP setup
To verify that NTP is setup correctly, Ansible checks that the ``systemd-timesyncd`` service is running. The builtin Ansible [``service``](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/service_module.html) module allows for service related functionality. Like the [package tasks](#check-package-installs), this block begins by gathering information about the system services.

To make sure NTP is setup for the right servers, the script ``cat``s the contents of ``/etc/systemd/timesyncd.conf`` to a variable and makes sure the line ``NTP=10.4.0.101 10.4.0.102`` is present. I hardcoded this value since it was the easiest way to do this for my purposes, but this could be refactored as a global variable for more flexibility.

Next, to make sure the NTP service is active, Ansible checks that ``systemd-timesyncd.service`` is running using the ``service`` facts which were gathered in the first task of the block.

#### Check rsync configuration
The last goal is to make sure an rsync script is installed and set to run every 15 minutes.

The builtin [``stat``](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/stat_module.html) module can be used to check if a file is present. Since the contents of this file are subject to change, I decided only to check that it exists in a predetermined location (in this case, ``/etc/scripts/rsync-pcap.sh``) rather than checking the content.

To ensure the script will run every 15 minutes, I again used the "``cat`` to a variable" technique, checking for the line ``*/15 * * * * /etc/scripts/rsync-pcap.sh`` in the file ``/var/spool/cron/crontabs/root``. This is the task for which super user access is necessary, as this location is usually protected. While Ansible does include a builtin [``cron``](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/cron_module.html) module, I found that under my circumstances, this was the simplest solution.

## For more information...
For more information about Ansible, be sure to check out the [Ansible documentation website](https://docs.ansible.com/ansible/latest/index.html). 

For more information about Liberty Eclipse, you can take a look at [the summary report from the 2017 version of the exercise](https://www.energy.gov/oe/articles/liberty-eclipse-exercise-summary-report).

For more information about other work the ITI has done, visit [the ITI webpage](https://iti.illinois.edu/).