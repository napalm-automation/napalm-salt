# napalm-salt
Modules for Salt, to retrieve, control, enforce and update configuration of network devices

Install Salt
============

Install Salt using the [platform-specific instructions](https://docs.saltstack.com/en/latest/topics/installation/#platform-specific-installation-instructions) from the official Saltstack documentation.
Be aware to install the master distribution **from the PPA repo**, as on the local server will run as Master, controlling the devices as Proxy minions.

Install NAPALM
==============

If NAPALM has never been installed on your system it will need to be before napalm-salt can work. The following steps are for an Ubuntu 16.04 installation:
```
sudo apt-get install libxml2-dev libxslt1-dev zlib1g-dev
sudo -H pip install napalm
```

Install NAPALM Salt
===================

Start by git cloning this repository and changing into the directory: ```git clone https://github.com/napalm-automation/napalm-salt.git && cd napalm-salt```.

Extract the SPM archive using the command: ```tar xf napalm-2016.3.spm``` or ```tar xf napalm-2016.11.spm``` for Salt ```>=2016.3``` or ```tar xf napalm.spm``` for older releases. When unpacking, a directory called ```napalm``` will be created.

Copy all its files and directories to the path specified as ```file_roots``` in the master config file (default is ```/etc/salt/states```), e.g. ```cp -r napalm/* /etc/salt/states```.

At the end, you should have a directory structure similar to the following under the ```file_roots``` directory (e.g.: ```/etc/salt/states```):

```
/etc/salt/states
├── top.sls
├── _proxy
|   └── napalm.py
├── _modules
|   ├── napalm_network.py
|   ├── napalm_ntp.py
|   ├── napalm_users.py
|   ├── napalm_bgp.py
|   ├── napalm_route.py
|   ├── napalm_snmp.py
|   └── napalm_probes.py
├── _grains
|   └── napalm.py
├── _states
|   ├── netntp.py
|   ├── netusers.py
|   ├── netsnmp.py
|   └── probes.py
├── _runners
|   └── ntp.py
├── router
    ├── init.sls
    ├── ntp.sls
    ├── users.sls
    ├── snmp.sls
    └── probes.sls
```

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

In ```/etc/salt/pillar/``` save a file called ```top.sls``` with the following content:

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

where:

  - core01.nrt01 is the name used to interact with the device, `salt 'core01.nrt01' test.ping`
  - ```/etc/salt/pillar/core01_nrt01.sls``` is the file containing the specifications of this device

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

  - DRIVER is the driver to be used when connecting to the device. For the complete list of supported operating systems, please check the [NAPALM readthedocs page](https://napalm.readthedocs.io/en/latest/#supported-network-operating-systems)
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

*** NOTE: *** make sure the pillar is a valid YAML file!

Also, double check if you can connect to the device from the server, using the credentials provided in the pillar.

If the errors persist, run the following lines in a Python console and ask in the Slack channel [#saltstack](https://networktocode.slack.com/messages/saltstack/) in [network.toCode()](https://networktocode.herokuapp.com/):

```python
>>> from napalm_base import get_network_driver
>>> d = get_network_driver('DRIVER')
>>> e = d('HOSTNAME', 'USERNAME', 'PASSWORD', optional_args={'config_lock': False})
>>> e.open()
>>> e.get_facts()
>>> e.close()
```

Running the master as a service
==============================

To configure the Salt master to run as a service and be easier to manage the process state, create the file ```/etc/systemd/system/salt-master.service``` with the following content:

```
[Unit]
Description=Salt Master
Requires=network.target
After=network.target

[Service]
Type=forking
PIDFile=/var/run/salt-master.pid
# ***NOTE*** the virtualenv here!  Your location may vary!
ExecStart=/usr/local/salt/virtualenv/bin/salt-master -d
Restart=on-failure
RestartSec=15

[Install]
WantedBy=multi-user.target
```

Start the Salt master
=======================

```bash
systemctl start salt-master
```

Depending on how your salt master is installed the location of the ```salt-master``` binary may need to be changed (the default location is a virtualenv). You should check the location of the binary with the ```which salt-master``` command.

Once the file is created and populated ```systemd``` will need to be reloaded with a ```systemctl daemon-reload``` to pick up the new unit. Do note that there may be an impact to reloading ```systemd``` so be careful.

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


Test your configuration
=======================

Once the key has been accepted, restart the proxy in debug mode and start a separate terminal session.  In your new terminal, issue the following command:
```
sudo salt 'core01.nrt01' test.ping
```
Substitute your DEVICE_ID for 'core01.nrt01'.  Output:
```
core01.nrt01:
    True
```
It should return `True` if there are no problems.  If everything checks out, hit <kbd>CTRL</kbd>+<kbd>C</kbd> and restart salt-proxy as a daemon.
```
sudo salt-proxy --proxyid=[DEVICE_ID] -d
```
Finally, sync your packages:
```
sudo salt core01.nrt01 saltutil.sync_all
```
As before, where 'core01.nrt01' is your DEVICE_ID.


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
  - [snmp](https://docs.saltstack.com/en/develop/ref/modules/all/salt.modules.napalm_snmp.html#module-salt.modules.napalm_snmp) module
  - [route](https://docs.saltstack.com/en/develop/ref/modules/all/salt.modules.napalm_route.html#module-salt.modules.napalm_route) module
  - [users](https://docs.saltstack.com/en/develop/ref/modules/all/salt.modules.napalm_users.html#module-salt.modules.napalm_users) module
  - [probes](https://docs.saltstack.com/en/develop/ref/modules/all/salt.modules.napalm_probes.html#module-salt.modules.napalm_probes) module

Few examples:

```bash
salt core01.nrt01 net.arp
salt core01.nrt01 net.mac
salt core01.nrt01 net.lldp
salt core01.nrt01 net.ipaddrs
salt core01.nrt01 net.interfaces
salt core01.nrt01 ntp.peers
salt core01.nrt01 ntp.set_peers 192.168.0.1 172.17.17.1 172.17.17.2
salt core01.nrt01 bgp.config  # returns the BGP configuration
salt core01.nrt01 bgp.neighbors  # provides statistics regarding the BGP sessions
salt core01.nrt01 snmp.config
salt core01.nrt01 route.show 1.2.3.4/24 bgp
salt core01.nrt01 probes.config
salt core01.nrt01 probes.results
salt core01.nrt01 net.commit
salt core01.nrt01 net.rollback
```

Configuration enforcement
=========================

To assure consistency across your network, [states](https://docs.saltstack.com/en/latest/topics/tutorials/starting_states.html) are your friend. To use a state is quite straight forwards when the module is already provided (examples in the next sections, for example [NTP](https://github.com/napalm-automation/napalm-salt#configuration-enforcement-for-ntp-peers-example)).
There are a couple of states already available, for:

  - [NTP](https://docs.saltstack.com/en/develop/ref/states/all/salt.states.netntp.html)
  - [SNMP](https://docs.saltstack.com/en/develop/ref/states/all/salt.states.netsnmp.html)
  - [Users](https://docs.saltstack.com/en/develop/ref/states/all/salt.states.netusers.html)
  - [Probes](https://docs.saltstack.com/en/develop/ref/states/all/salt.states.netntp.html)


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

Now, when running the command below, Salt will check if on your device the NTP peers are setup as specified in the Pillar file. If not, will add the missing NTP peers and will remove the excess. Thus, at the end of the operation, the list of NTP peers configured on the device will match NTP peers listed in the Pillar.

```bash
salt core01.nrt01 state.sls router.ntp
```

Configuration enforcement for SNMP (Example)
============================================

In the pillar file of the device append the following lines:

```yaml
snmp.config:
  contact: <email addr>
  location: <location>
  community: <community name>
```

Example:

```yaml
snmp.config:
  contact: noc@yourcompany.com
  location: San Jose, CA, US
  community: super-safe
```

Executing the state as following, will update the SNMP configuration on your device:

```bash
salt core01.nrt01 state.sls router.snmp
```

Scheduled states: maintaining configuration updated
===================================================

Using the capabilities of the states and [the schedulers](https://docs.saltstack.com/en/latest/ref/states/all/salt.states.schedule.html#management-of-the-salt-scheduler) you can ensure the configuration on the device is consistent and up-to-date.

Yes, you don't need to jump in a box and manualluy execute a command or add aliases etc. 5 lines of config is all you need to write:

Example:

In the master config file:

```yaml
schedule:
  ntp_config:
    function: state.sls
    args: router.ntp
    returner: smtp
    days: 1
```

Where:

- ```ntp_config``` is just the name of the scheduled job - can be anything
- ```function``` - this is how tell Salt that a state will be executed
- ```args``` - specify the name of the state
- ```returner``` (optional) - you can forward the output of the state to a different service. In this case SNMP - will send an email to a specific address with the summary of the state. There are [many other returners available](https://docs.saltstack.com/en/latest/ref/returners/#full-list-of-returners)
- ```days``` - how often to check & update the config. Other options are: ```seconds```, ```minutes```, ```hours``` etc...


Other modules:
==============

Salt comes with many flavours of modules - complete reference at [https://docs.saltstack.com/en/latest/ref/index.html](https://docs.saltstack.com/en/latest/ref/index.html).

There are few other features, such [reactor](https://docs.saltstack.com/en/latest/topics/reactor/). The reactor system allows you to execute commands after an event happened, based on its output.
