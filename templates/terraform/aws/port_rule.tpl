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

# CREATING SECURITY_GROUP
resource "aws_security_group" "{{ infra_element_name ~ "_security_group" }}" {
  name        = "{{ infra_element_name }}"
  vpc_id      = aws_vpc.{{extra_parameters.networks[0].infra_element_name}}.id
{%- for key, value in context().items() %}{% if not callable(value)%} {%if value.kind and value.kind is defined %}
  {% if value == "INGRESS" %}ingress{% else %}egress{%- endif %} {
    from_port   = {{ value.fromPort }}
    to_port     = {{ value.toPort }}
    protocol = "{{ value.protocol }}"
    cidr_blocks = [{% for range in value.cidr %}"{{ range }}", {% endfor %}]
  }
{%- endif %}{% endif %}{% endfor %}
}

{#  {% for net_el in extra_parameters["networks"] %}{% for sub_el in net_el %}{%- if sub_el.endswith(value["belongsTo"]) %}    vpc_id      = aws_vpc.{{net_el.infra_element_name}}.id ##MISSING VPC NAME REFERENCE FROM DOML
{%- endif %}{% endfor %}{% endfor %}
#}