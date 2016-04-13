# napalm-salt
Modules for Salt, to retrieve, control, enforce and update configuration of network devices

Install Salt
============

Install Salt using the [platform-specific instructions](https://docs.saltstack.com/en/latest/topics/installation/#platform-specific-installation-instructions) from the official Saltstack documentation.
Be aware to install the master distribution, as on the local server will run as Master, controlling the devices as Proxy minions.

Install NAPALM Salt
===================

Download the file __napalm.spm__ and unpack using the command: ```spm local install napalm.spm```


Configure Salt Master & Proxy
=============================

There are two configuration files needed to make Salt run as proxy-master: ```master``` and ```proxy```. The files provided as example will configure a default running evironment, for more specific options, please check the documentation or the comments inside!

Cofigure the connection with a device
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
# systemctl start salt-master
```

Start the proxy minion for your device
======================================

```bash
# systemctl start salt-proxy@[DEVICE_ID]
```

Example:

```bash
# systemctl start salt-proxy@edge01.nrt01
```

Start using Salt
================

Everything is setup now, you need just to start issuing commands to retieve/set properties.

Syntax:

```bash
# salt [DEVICE_ID] [FUNCTION]
```

For the updated list of functions, check the following resources:
  - [net](https://docs.saltstack.com/en/develop/ref/modules/all/salt.modules.napalm_network.html#module-salt.modules.napalm_network) mdoule
  - [ntp](https://docs.saltstack.com/en/develop/ref/modules/all/salt.modules.napalm_ntp.html#module-salt.modules.napalm_ntp) module

Few examples:

```bash
# salt core01.nrt01 ntp.peers
# salt core01.nrt01 net.arp
# salt core01.nrt01 net.interfaces
# salt core01.nrt01 ntp.set_peers 192.168.0.1 172.17.17.1 172.17.17.2
# salt core01.nrt01 net.commit
# salt core01.nrt01 net.rollback
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
# salt core01.nrt01 state.sls router.ntp
```

Salt can be also [instructed](https://docs.saltstack.com/en/latest/ref/states/all/salt.states.schedule.html#management-of-the-salt-scheduler) to constantly perform this operation and ensure the configuration on the device is consistent and up-to-date.
