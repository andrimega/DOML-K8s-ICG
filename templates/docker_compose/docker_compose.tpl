version: '3'
services:
  {{ name }}:
    {%- for image in extra_parameters %}{% if image.maps is sameas generatedFrom %}
    image: {{ image.uri }}
    {% endif %}{%- endfor %}
    restart: on-failure
    ports:
    {%- for config in hostConfigs[0]["configurations"] %}
    - "{{ config.container_port }}:{{ config.vm_port }}"
    {%- endfor %}
    {%- if hostConfigs[0]["environment_variables"] is defined %}
    environment:
    {%- for variable in hostConfigs[0]["environment_variables"] %}
    - {{ variable.key }}="{{ variable.value }}"
    {%- endfor %}
    {%- endif %}
{%- if networks is defined %}
    networks:
      - {{ networks.0.name }}

networks:
  {{ networks.0.name }}:
    name: {{ networks.0.containerNetworkName }}
{%- endif %}
