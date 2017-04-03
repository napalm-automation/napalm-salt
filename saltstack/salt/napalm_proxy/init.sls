/etc/salt/proxy:
  file.managed:
    - name: /etc/salt/proxy
    - source: salt://napalm_proxy/proxy.conf
    - user: root
    - group: root
    - mode: 644

{% for switch in ['veos1', 'veos2', 'veos3'] -%}
salt-proxy-configure-{{ switch }}:
  salt_proxy.configure_proxy:
    - proxyname: {{ switch }}
    - start: True
    - require:
      - pip: napalm-junos
{% endfor %}

zlib1g-dev:
  pkg.installed

python-dev:
  pkg.installed

python-pip:
  pkg.installed

libxslt1-dev:
  pkg.installed

libffi-dev:
  pkg.installed

libssl-dev:
  pkg.installed

napalm-junos:
  pip.installed:
    - name: napalm-junos
    - require:
      - pkg: python-pip
      - pkg: libssl-dev
      - pkg: libffi-dev
      - pkg: libxslt1-dev
      - pkg: python-dev

napalm-eos:
  pip.installed:
    - name: napalm-eos
    - require:
      - pip: napalm-junos

capirca:
  pip.installed:
    - name: capirca
    - editable: git+https://github.com/google/capirca.git#egg=aclgen
