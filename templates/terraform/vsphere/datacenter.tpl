{##-------- Variables ##}
{%- set preexinsting = preexisting -%}
{%- if preexinsting %}
data "vsphere_datacenter" "{{datacenter}}" {
  name = "{{datacenter}}"
}
{%- else %}
resource "vsphere_datacenter" "{{datacenter}}" {
  name   = "{{datacenter}}"
  folder = "{{folder_path}}"
}
{%-endif %}