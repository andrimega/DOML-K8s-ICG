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


[{{ "servers_for_" ~ name }}]
{%- for image in extra_parameters %}{% if image["maps"] is sameas generatedFrom["name"] %}{% for cont in image["generatedContainers"] %}{% if cont["name"] is sameas name %}{% if "hostConfigs" in cont %}
{% raw %}{{ instance_server_public_ip_{% endraw %}{{ cont.hostConfigs.0.host }} {% raw %}}}{% endraw %}
{%- endif %}{% endif %}{% endfor %}{% endif %}{%- endfor %}

[{{ "servers_for_" ~ name }}:vars]
ansible_connection=ssh
ansible_user=centos
ansible_ssh_private_key_file=ssh_key