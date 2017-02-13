{% set probes_config = pillar.get('probes.config', {}) -%}
{% set probes_defaults = pillar.get('probes', {}) %}

cf_probes:
  probes.managed:
    - probes  : {{probes_config}}
    - defaults: {{probes_defaults}}
