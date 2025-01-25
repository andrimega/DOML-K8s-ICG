{%- if preexisting %}
data "vsphere_datastore" "{{name}}" {
  name          = "{{vsphere_datastore_name}}"
{%- for key, value in context().items() %}{% if value is mapping%}{% if value.type == "vsphere_datacenter"%}
  datacenter_id = "${data.vsphere_datacenter.{{value.name}}.id}" {% endif %}{% endif %}{% endfor %}
}
{%- endif %}