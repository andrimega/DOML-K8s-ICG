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
[local]
127.0.0.1

[local:vars]
ansible_connection=local
{%- for node in nodes %}
instance_server_public_ip_{{ node.infra_element_name }}={% raw %}{{ instance_server_public_ip_{% endraw %}{{ node.infra_element_name }} {% raw %}}}{% endraw %}
{%- endfor %}

[{{ "servers_for_" ~ name }}]
{%- for node in nodes %}
{% raw %}{{ instance_server_public_ip_{% endraw %}{{ node.infra_element_name }} {% raw %}}}{% endraw %} doml_element_name={{ node.infra_element_name }} doml_element_type={{ node.vm_flavor }}
{%- endfor %}

[{{ "servers_for_" ~ name }}:vars]
ansible_connection=ssh
{%- if nodes[0].template is defined %}
ansible_user=root
{%- else %}
ansible_user=centos
{%- endif %}
ansible_ssh_private_key_file=ssh_key
