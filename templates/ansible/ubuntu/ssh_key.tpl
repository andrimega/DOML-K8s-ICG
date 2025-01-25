{%- for node in nodes %}
{%- raw %}{{ instance_server_private_key_{% endraw %}{{ node.credentials }}{% raw %}_{%- endraw %}{{node.infra_element_name}}{% raw %}}}
{% endraw %}
{%- endfor %}