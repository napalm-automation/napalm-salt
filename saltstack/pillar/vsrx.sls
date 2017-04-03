{% set hostname = salt['grains.get']('id', '') %}
proxy:
  proxytype: napalm
  driver: junos
  host: {{ hostname }}
  username: vagrant
  passwd: Vagrant
  optional_args:
    config_lock:
      - False

ntp.peers:
  - 192.168.50.1
