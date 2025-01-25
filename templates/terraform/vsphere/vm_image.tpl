{%- if preexisting %}
data "vsphere_virtual_machine" "{{name}}" {
  name = "{{image_name}}"
{%- for key, value in context().items() %}{% if value is mapping%}{% if value.type == "vsphere_datacenter"%}
  datacenter_id = "${data.vsphere_datacenter.{{value.name}}.id}"{% endif %}{% endif %}{% endfor %}
}
{%- endif %}