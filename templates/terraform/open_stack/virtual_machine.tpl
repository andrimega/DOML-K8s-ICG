{# Copyright 2022 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#-------------------------------------------------------------------------
#}
{%- set preexinsting = extra_parameters["networks"]["preexisting"] -%}

# Create virtual machine
resource "openstack_compute_instance_v2" "{{ infra_element_name }}" {
  name        = "{{ name }}"
  image_name  = "{{ os }}"
  flavor_name = "{% if 'sizeDescription' in context().keys() %}{{ sizeDescription }}{% elif 'vm_flavor' in context().keys() %}{{ vm_flavor }}{% else %}{{ instance_type }}{% endif %}"
  key_pair    = openstack_compute_keypair_v2.{{ credentials }}.name
{%- if 'BProperty_config_drive' in context().keys() %}
  config_drive = true 
{%- endif %}
  {%- for key, value in context().items() %}{% if not callable(value)%}{%- if key.startswith('NetworkInterface') %}
  network {
    port = openstack_networking_port_v2.{{ value.name ~ "_networking_port"}}.id
  }
  {%- endif %}{% endif %}{%- endfor %}
}

{% if not "configInterface" in context().keys() %}
# Create floating ip
resource "openstack_networking_floatingip_v2" "{{infra_element_name ~ "_floating_ip"}}" {
  pool = "external"
  # fixed_ip = "{{ address }}"
}

# Attach floating ip to instance
resource "openstack_compute_floatingip_associate_v2" "{{ infra_element_name ~ "_floating_ip_association" }}" {
  floating_ip = openstack_networking_floatingip_v2.{{ infra_element_name ~ "_floating_ip" }}.address
  instance_id = openstack_compute_instance_v2.{{ infra_element_name }}.id
}
{% endif %}

{% for key, value in context().items() %}{% if not callable(value)%}{%- if key.startswith('NetworkInterface') %}

{%- if value.associated is not defined %}
# Retrive default security group
data "openstack_compute_secgroup_v2" "default" {
  name = "default"
}
{%- endif %}

{# adding security groups for interfaces #}
# Attach networking port
resource "openstack_networking_port_v2" "{{ value.name ~ "_networking_port" }}" {
  name           = "{{ value.name }}"
  admin_state_up = true
{# Condition for security group association to networking port, if not define use default, if defined and doml older then 3.0 use string, if defined and doml version 3.1 or newer use element from list #}
{%- if value.associated is defined %}{% if value.associated is string %}  security_group_ids = [ openstack_compute_secgroup_v2.{{ value.associated }}.id ]
{# TODO if more than one security group is associated to the networking port to add for cicle to take all sec_groups #}
{%- else %}  security_group_ids = [ openstack_compute_secgroup_v2.{{ value.associated[0].name }}.id ]{% endif %} {#  security_group_ids = [ {% for i in value["associated"] %}openstack_compute_secgroup_v2.{{ i.name }}.id {% endfor %}] #}
{%- else %}  security_group_ids = [ openstack_compute_secgroup_v2.default.id ]
{%- endif %}
{%- for net_el in extra_parameters["networks"] %}{%- for sub_el in net_el["subnets"] %}{% if sub_el["maps"] is sameas value["belongsTo"] %}{%- if net_el["preexisting"] is sameas true %}
  network_id = data.openstack_networking_network_v2.{{ net_el.infra_element_name }}.id
  fixed_ip {
{%- if sub_el["preexisting"] is sameas true %}
   subnet_id = data.openstack_networking_subnet_v2.{{ sub_el.name ~ "_subnet" }}.id
{%- else %}
   subnet_id = openstack_networking_subnet_v2.{{ sub_el.name ~ "_subnet" }}.id
{%- endif %}
  }
{%- else %}
  network_id = openstack_networking_network_v2.{{ net_el.infra_element_name }}.id
  fixed_ip {
   subnet_id = openstack_networking_subnet_v2.{{ sub_el.name ~ "_subnet" }}.id
  }
{%- endif %}{% endif %}{% endfor %}{%- endfor %}
}

resource "openstack_compute_interface_attach_v2" "{{ infra_element_name ~ "_port_association" }}" {
  instance_id = openstack_compute_instance_v2.{{ infra_element_name }}.id
  port_id = openstack_networking_port_v2.{{ value.name ~ "_networking_port" }}.id
}{% endif %}{% endif %}{% endfor %}