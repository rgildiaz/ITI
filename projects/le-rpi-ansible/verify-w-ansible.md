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

``hosts: remote`` asks Ansible to use the ``[remote]`` group which is specified in the inventory file (gathered from ``ansible.cfg`` to be ``le-rpi-hosts``). As you might guess, ``remote_user: manager`` and ``become: yes`` ask Ansible to connect to the hosts as the user ``manager`` and to attempt to gain super user access (this is important for some of the later tasks).

### The Playbook
In [``rpi-installs.yml``](./rpi-installs.yml), take a look at the ``tasks:`` block to see the actions that Ansible takes on host systems.

The main goals of this playbook are to:
1. Make sure all the necessary packages are installed,
2. Verify that and NTP time server is setup,
3. Ensure an rsync script is in place and running, and

You might see that I've organized these goals into blocks, so I will go through them one-by-one.

#### Check package installs
When designing this section of the script, I wanted it to be easy to maintain and manage. I decided that the easiest way to do this would be to iterate over a list of packages which can easily be edited.

First, in order to work with packages, I chose to use Ansible's builtin [``package``](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/package_module.html) module. The first task in this block is to gather the facts about the packages on the system, which will allow Ansible to see information about them.

Next, to store a list of packages which are not installed (which will later be printed), store an empty list in a global variable called ``not_found_packages``.

I found that the easiest way to work with a list of packages would be to use a [loop](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/items_lookup.html) which looks up the contents of ``vars/packages.txt``. In order for this to work cleanly, I used the [``include_tasks``](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/include_tasks_module.html) module, which allows for the execution of tasks which are stored outside the current playbook. In this case, the set of tasks which will be executed for each item in ``packages.txt`` is located at [``tasks/package-tasks.yml``](tasks/package_tasks.yml).

``package-tasks.yml`` fails if it can't find the package it is given. The failure is caught by the ``rescue: `` block, which adds it to the list of failed packages.

There are some items which cannot be checked with the ``package`` module. To avoid bloat in the main playbook, tasks which manually check for these are stored in [``tasks/manual_package_tasks.yml``](tasks/manual_package_tasks.yml).

My process for manually checking packages which might not be found is just to call their ``--version`` option and check that the output matches a predefined value (e.g. ``ryu 4.34``)

Once all the packages have been checked, print the list of those which were not found.

#### Check NTP setup
To verify that NTP is setup correctly, I decided to check that the ``systemd-timesyncd`` service is running. To do so, I used the builtin Ansible [``service``](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/service_module.html) module. Like the [package tasks](#check-package-installs), this block begins by gathering information about the system services.

To make sure NTP is setup for the right servers, the script simply ``cat``s the contents of ``/etc/systemd/timesyncd.conf`` to a variable and makes sure the line ``NTP=10.4.0.101 10.4.0.102`` is present. I hardcoded this value since it needs to be set this way for all the systems I was verifying, but this could be refactored as a global variable. 

Next, to make sure the NTP service is active, we check that ``systemd-timesyncd.service`` is running.

#### Check rsync configuration
The last task is to make sure an rsync script is installed and set to run every 15 minutes.

To make sure the script is installed, I use the builtin [``stat``](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/stat_module.html) module, which can be used to check if a file is present. Since the contents of this file are subject to change, I decided only to check that it is present in a predetermined location (in this case, ``/etc/scripts/rsync-pcap.sh``) rather than checking the contents themselves.

To ensure the script will run every 15 minutes, I again used the "``cat`` to a variable" technique, checking for the line ``*/15 * * * * /etc/scripts/rsync-pcap.sh`` in the file ``/var/spool/cron/crontabs/root``. This is the task for which super user access is necessary, as this location is usually protected. While Ansible does include a builtin [``cron``](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/cron_module.html) module, I found that under my circumstances, this was the simplest solution.

## For more information...
I hope this is useful for tracing my methodology and thoughts throughout this process. If you find errors or have suggestions for improvement, I would appreciate any feedback or comments!

For more information about Ansible, be sure to check out the [Ansible documentation website](https://docs.ansible.com/ansible/latest/index.html). 

For more information about Liberty Eclipse, you can take a look at [the summary report from the 2017 version of the exercise](https://www.energy.gov/oe/articles/liberty-eclipse-exercise-summary-report).

For more information about other work the ITI has done, visit [the ITI webpage](https://iti.illinois.edu/).