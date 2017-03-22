{% set hostname = salt['grains.get']('id', '') %}
proxy:
  proxytype: napalm
  driver: eos
  host: {{ hostname }}
  username: admin
  passwd: admin
