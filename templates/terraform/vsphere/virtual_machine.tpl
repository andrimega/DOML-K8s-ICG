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

variable "username" {
  type = string
  default = "esilab"
}

variable "password" {
  type = string
  default = "NoNeedForSpecialChars04392"
}

# Create virtual machine
resource "vsphere_virtual_machine" "{{ infra_element_name }}" {
  name        = "{{ name }}"
{%- if pool and pool.preexisting %}
  resource_pool_id  = "${data.{{pool.type}}.{{ pool.name }}.id}"{%- endif %}
{%- if datastore and datastore.preexisting %}
  datastore_id = "${data.vsphere_datastore.{{ datastore.name }}.id}"{%- endif %}
  num_cpus = {% if 'vm_Virtual_CPU_Cores' in context().keys() %}{{ vm_Virtual_CPU_Cores }}{% else %}{{ cpu_count }}{% endif %}
  memory   = {% if 'vm_Memory' in context().keys() %}{{ vm_Memory }}{% else %}{{ memory_mb }}{% endif %}

  guest_id = "{{guest_id}}"

  network_interface {
    network_id = {%- for key, value in context().items() %}{% if not callable(value)%}{%if key.startswith('NetworkInterface') %} "${data.vsphere_network.{{ value.belongsTo }}.id}"{%- endif %}{% endif %}{% endfor %}
  }

  disk {
{% for store_el in extra_parameters["storages"] %}
    label = "{{ store_el.label }}"
    size  = "{{ store_el.size_gb }}"
{% endfor %}   
  }

  clone {
    template_uuid = "${data.vsphere_virtual_machine.{{template.name}}.id}"
    customize {
      linux_options {
        host_name = "{{host_name}}"
        domain    = "{{domain}}"
      }
      network_interface {
        ipv4_address = {%- for key, value in context().items() %}{% if not callable(value)%}{%if key.startswith('NetworkInterface') %} "{{ value.endPoint }}"{%- endif %}{% endif %}{% endfor %}
        ipv4_netmask = 27
        dns_server_list = ["10.81.34.36, 10.81.34.60"]
      }
      ipv4_gateway = "10.83.18.65"
    }
  }

  connection {
    type     = "ssh"
    user     = "${var.username}"
    password = "${var.password}"
    host     = "${self.default_ip_address}" 
  }

  provisioner "remote-exec"  {
    inline = [
      "systemctl stop firewalld",
      "echo 'nameserver 10.81.34.36' | sudo tee /etc/resolv.conf",
      "mkdir /root/.ssh",
      "chmod 700 /root/.ssh",
      "touch /root/.ssh/authorized_keys",
      "chmod 600 /root/.ssh/authorized_keys",
      "echo -e '${tls_private_key.{{ credentials }}.public_key_openssh}' >> /root/.ssh/authorized_keys"
    ]
  }
}