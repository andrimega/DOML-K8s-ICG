{##-------- Variables ##}
{%- set preexinsting = preexisting -%}
{%- if  preexinsting %}
data "vsphere_network" "{{infra_element_name}}" {
  name          = "{{vsphere_network_name}}"
{%- for key, value in context().items() %}{% if value is mapping%}{% if value.type == "vsphere_datacenter"%}
  datacenter_id = "${data.vsphere_datacenter.{{value.name}}.id}" {% endif %}{% endif %}{% endfor %}
}
{% else %}
TODO
{%-endif %}