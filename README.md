# napalm-salt
Modules for Salt, to retrieve, control, enforce and update configuration of network devices

Install Salt
============

Install Salt using the [platform-specific instructions](https://docs.saltstack.com/en/latest/topics/installation/#platform-specific-installation-instructions) from the official Saltstack documentation.
Be aware to install the master distribution, as on the local server will run as Master, controlling the devices as Proxy minions.

Install NAPALM
==============

If NAPALM has never been installed on your system it will need to be before napalm-salt can work. The following steps are for an Ubuntu 16.04 installation:
```
sudo apt-get install libxml2-dev libxslt1-dev zlib1g-dev
sudo -H pip install napalm
```

Install NAPALM Salt
===================

Start by git cloning this repository and changing into the directory: ```git clone https://github.com/napalm-automation/napalm-salt.git && cd napalm-salt```
Extract the __napalm.spm__ file using the command: ```tar xf napalm.spm```
The module can now be built using the Salt Package Manager (spm): ```spm build napalm```
With the module built the final step is to install it with: ```sudo spm local install /srv/spm_build/napalm-*.spm```

Configure Salt Master & Proxy
=============================

There are two configuration files needed to make Salt run as proxy-master: ```master``` and ```proxy```. The files provided as example will configure a default running environment used for the rest of this guide. Place the ```master``` and ```proxy``` files in ```/etc/salt/```. For more specific options, please check the documentation or the comments inside!

*** NOTE: ***
If you do not use the provided ```proxy``` file the following two options are required to be in the ```proxy``` file for the minion to work:

```
master: localhost
multiprocessing: False
```

Configure the connection with a device
======================================

In ```/etc/salt/pillar``` save a file called ```top.sls``` with the following content:

```yaml
base:
  [DEVICE_ID]:
    - [DEVICE_SLS_FILENAME]
```

where:

  - DEVICE_ID will be the name used to interact with the device, from the CLI of the server
  - DEVICE_SLS_FILENAME is the name of the file containing the specifications of the device

Example:

```yaml
base:
  core01.nrt01:
    - core01_nrt01
```

Then you need to add content in the device descriptor file ```[DEVICE_SLS_FILENAME].sls``` (called _Pillar_):

```yaml
proxy:
  proxytype: napalm
  driver: [DRIVER]
  host: [HOSTNAME]
  username: [USERNAME]
  passwd: [PASSWORD]
```

where:

  - DRIVER is the driver to be used when connecting to the device. For the complete list of supported operating systems, please check the [NAPALM readthedocs page](http://napalm.readthedocs.org/en/latest/#supported-network-operating-systems)
  - HOSTNAME, USERNAME, PASSWORD are the connection details

Example ```core01_nrt01.sls```:

```yaml
proxy:
  proxytype: napalm
  driver: iosxr
  host: core01.nrt01
  username: my_username
  passwd: my_password
```

Start the Salt master
=======================

Issue the following command on the same server you just installed the Salt master:

```bash
systemctl start salt-master
```

Start the proxy minion for your device
======================================

Start with testing proxy minion:
```bash
sudo salt-proxy --proxyid=[DEVICE_ID] -l debug
```

On the first connection attempt you will find the that minion cannot talk and is stuck with the following error message:
```
[ERROR   ] The Salt Master has cached the public key for this node, this salt minion will wait for 10 seconds before attempting to re-authenticate
[INFO    ] Waiting 10 seconds before retry.
```
This is normal and is due to the salt key from the minion not being accepted by the master. Quit the minion with <kbd>CTRL</kbd>+<kbd>C</kbd> and run ```sudo salt-key```. Under ```Unaccepted Keys:``` you should see your ```[DEVICE_ID]```. Accept the key with ```sudo salt-key -a [DEVICE_ID]```. Now rerun the minion debug and you should see the minion connecting to your device.

Running the proxy minion as a service
=====================================

To configure the minion to run as a service create the file ```/etc/systemd/system/salt-proxy@.service``` with the following:

```
[Unit]
Description=Salt proxy minion
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/salt-proxy -l debug --proxyid %I
User=root
Group=root
Restart=always
RestartPreventExitStatus=SIGHUP
RestartSec=5

[Install]
WantedBy=default.target
```

Depending on how your salt master is installed the location of the ```salt-proxy``` binary may need to be changed. You can look up the location of the binary with the ```which salt-proxy``` command. Also the logging level is set to debug with the ```-l debug``` switch. This is useful for troubleshooting however you may want to remove this.

Once the file is created and populated ```systemd``` will need to be reloaded with a ```systemctl daemon-reload``` to pick up the new unit. Do note that there may be an impact to reloading ```systemd``` so be careful.

The minion can now be started with:

```bash
systemctl start salt-proxy@[DEVICE_ID]
```

For example:

```bash
systemctl start salt-proxy@edge01.nrt01
```

Start using Salt
================

Everything is setup now, you need just to start issuing commands to retieve/set properties.

Syntax:

```bash
salt [DEVICE_ID] [FUNCTION]
```

For the updated list of functions, check the following resources:
  - [net](https://docs.saltstack.com/en/develop/ref/modules/all/salt.modules.napalm_network.html#module-salt.modules.napalm_network) mdoule
  - [ntp](https://docs.saltstack.com/en/develop/ref/modules/all/salt.modules.napalm_ntp.html#module-salt.modules.napalm_ntp) module
  - [bgp](https://docs.saltstack.com/en/develop/ref/modules/all/salt.modules.napalm_bgp.html#module-salt.modules.napalm_bgp) module
  - [probes](https://docs.saltstack.com/en/develop/ref/modules/all/salt.modules.napalm_probes.html#module-salt.modules.napalm_probes) module

Few examples:

```bash
salt core01.nrt01 ntp.peers
salt core01.nrt01 net.arp
salt core01.nrt01 net.interfaces
salt core01.nrt01 ntp.set_peers 192.168.0.1 172.17.17.1 172.17.17.2
salt core01.nrt01 bgp.config  # returns the BGP configuration
salt core01.nrt01 bgp.neighbors  # provides statistics regarding the BGP sessions
salt core01.nrt01 probes.results
salt core01.nrt01 net.commit
salt core01.nrt01 net.rollback
```

Configuration enforcement for NTP peers (Example)
=================================================

In the Pillar file of the device append the following lines:

```yaml
ntp.peers:
  - [PEER1]
  - [PEER2]
  - ...
```

Example:

```yaml
ntp.peers:
  - 192.168.0.1
  - 172.17.17.1
```

In ```/etc/salt/states``` create a directory (say ```router``` for example). Inside this directory, create a file called ```init.sls```, having the following content:

```
include:
  - .ntp
```

Inside the file ```ntp.sls``` add the following content:

```yaml
{% set ntp_peers = pillar.get('ntp.peers', {}) -%}

cf_ntp:
  netntp.managed:
    - peers: {{ntp_peers}}
```

Now, when running the command below, Salt will check if on your device the NTP peers are setup as specified in the Pillar file. If not, will add the missing NTP peers and will remove the excess. Thus, at the end of the operation, the list of NTP peers configured on the device will match NTP peers listed in the Pillar.

```bash
salt core01.nrt01 state.sls router.ntp
```

Salt can be also [instructed](https://docs.saltstack.com/en/latest/ref/states/all/salt.states.schedule.html#management-of-the-salt-scheduler) to constantly perform this operation and ensure the configuration on the device is consistent and up-to-date.
