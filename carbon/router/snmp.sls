{% set default_snmp = pillar.get('snmp', {}) -%}
{% set device_snmp = pillar.get('snmp.config', {}) -%}

cf_snmp:
  snmp.managed:
    - config: {{device_snmp}}
    - defaults: {{default_snmp}}
