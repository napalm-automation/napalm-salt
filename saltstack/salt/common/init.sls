/etc/hosts:
  file.managed:
    - name: /etc/hosts
    - source: salt://common/hosts
    - user: root
    - group: root
    - mode: 644
