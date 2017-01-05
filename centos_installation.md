## Install Salt-Master & napalm on CentOS 7

This guide assumes that you have a freshly installed CentOS 7 (minimal)

#### Import salt's GPG public key
```
rpm --import https://repo.saltstack.com/yum/redhat/7/x86_64/latest/SALTSTACK-GPG-KEY.pub
```

#### Add the saltstack repo file to your system
vi `/etc/yum.repos.d/saltstack.repo`
```
[saltstack-repo]
name=SaltStack repo for CentOS $releasever
baseurl=https://repo.saltstack.com/yum/redhat/$releasever/$basearch/latest
gpgkey=https://repo.saltstack.com/yum/redhat/$releasever/$basearch/latest/SALTSTACK-GPG-KEY.pub
enabled=1
gpgcheck=1
```
#### Install Salt packages on your system
```
yum update -y
yum install -y salt-master salt-minion salt-ssh salt-syndic salt-cloud salt-api
```

#### Install napalm on your system
##### Prerequisites
```
yum install epel-release
yum install -y python-pip
yum install libxml2-devel libxslt-devel zlib-devel gcc openssl-devel libffi-devel python-devel
```
```
pip install napalm
```

#### Configure the system
##### Backup the original Configuration files
```
mv /etc/salt/proxy /etc/salt/proxy.original
mv /etc/salt/master /etc/salt/master.original
```
Copy-paste the master & proxy files from this dir inside /etc/salt

##### Create the pillar dir
Here you will add the
```
mkdir -p /etc/salt/pillar
```

Create the file ```top.sls``` with the following content:

```yaml
base:
  [DEVICE_ID]:
    - [DEVICE_SLS_FILENAME]
```

where:

  - DEVICE_ID will be the name used to interact with the device, from the CLI of the server
  - DEVICE_SLS_FILENAME is the name of the file containing the specifications of the device


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

 Make sure the pillar is a valid **YAML** file!

Also, double check if you can connect to the device from the server, using the credentials provided in the pillar.

##### Example
```
tree /etc/salt/pillar/
/etc/salt/pillar/
├── top.sls
└── vsrx_demo.sls
```
top.sls
```yaml
base:
  vsrx.demo:
    - vsrx_demo
```
vsrx_demo.sls
```yaml
proxy:
  proxytype: napalm
  driver: junos
  host: <device IP>
  username: <device username>
  passwd: <device password>
```

If the errors persist, run the following lines in a Python console and ask in the Slack channel [#saltstack](https://networktocode.slack.com/messages/saltstack/) in [network.toCode()](https://networktocode.herokuapp.com/):

```python
>>> from napalm_base import get_network_driver
>>> d = get_network_driver('DRIVER')
>>> e = d('HOSTNAME', 'USERNAME', 'PASSWORD', optional_args={'config_lock': False})
>>> e.open()
>>> e.get_facts()
>>> e.close()
```
#### Restart salt-master & check service status
```
systemctl restart salt-master
systemctl status salt-master
```

Open a second terminal window and connect to Salt-Master again.

On the first terminal start the proxy process in debug mode
```salt-proxy --proxyid=vsrx.demo -l debug```

You will see the following message
```
[INFO    ] Waiting 10 seconds before retry.
[ERROR   ] The Salt Master has cached the public key for this node, this salt minion will wait for 10 seconds before attempting to re-authenticate
```

On the second terminal type ```salt-key -L```. You sould see the following output.
```
Accepted Keys:
Denied Keys:
Unaccepted Keys:
vsrx.demo
Rejected Keys:
```

Type ```salt-key  -A``` and accept the key. Now the proxy process can authenticate against the Salt-Master.

You are ready to go!
