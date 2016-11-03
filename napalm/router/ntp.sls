{% set ntp_peers = pillar.get('ntp.peers', {}) -%}
{% set ntp_servers = pillar.get('ntp.servers', {}) -%}

cf_ntp:
  netntp.managed:
    - peers: {{ntp_peers}}
    - servers: {{ntp_servers}}

