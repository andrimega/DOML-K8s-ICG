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

resource "aws_instance" "{{infra_element_name}}" {
{% for image_el in extra_parameters["vmImages"] %}{%- if image_el["infra_element_name"] == generatedFrom %}  ami = "{{ image_el.image_name }}"{%- endif %}{% endfor %}
  instance_type = "{% if 'vm_flavor' in context().keys() %}{{ vm_flavor }}{% else %}{{ instance_type }}{% endif %}"
  key_name = "{{credentials}}"
  {% if 'group' in context().keys() %}vpc_security_group_ids = [aws_security_group.{{group ~ "_security_group"}}.id]{% endif %}
  tags = {
    "Name" = "{{name}}"
  }
}
