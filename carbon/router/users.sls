{% set default_users = pillar.get('users', {}) -%}
{% set device_users = pillar.get('users.config', {}) -%}

cf_users:
  netusers.managed:
    - users: {{device_users}}
    - defaults: {{default_users}}
