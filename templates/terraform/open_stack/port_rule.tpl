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
resource "openstack_compute_secgroup_v2" "{{infra_element_name}}" {
    name = "infra_element_name"
    description = "PIACERE security group created - {{infra_element_name}}"

    {%- for key, value in context().items() %}{% if not callable(value)%} {%if value.kind and value.kind is defined %}
    rule {
        from_port   = {{ value.fromPort }}
        to_port     = {{ value.toPort }}
        ip_protocol = "{{ value.protocol }}"
        cidr        = {% for range in value.cidr %}"{{ range }}"{% endfor %}
    }
    {%- endif %}{% endif %}{% endfor %}
}

