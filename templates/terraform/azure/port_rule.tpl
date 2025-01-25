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

resource "azurerm_network_security_group" " {{ infra_element_name ~ "_security_group" }}" {
  name                = " {{ infra_element_name }}"
  location            = azurerm_resource_group. {{ resource_name }}.location
  resource_group_name = azurerm_resource_group. {{ resource_name }}.name
  {%- for key, value in context().items() %}{% if not callable(value)%} {%if value.kind and value.kind is defined %}
  security_rule {
    name                       = "{{ value.name }}"
    priority                   = 100
    direction                  = "{% if value == "INGRESS" %} Inbound {% else %} Outbound {% endif %} "
    access                     = "Allow"
    protocol                   = "{{ value.protocol }}""
    source_port_range          = {{ value.fromPort }}"
    destination_port_range     = "{{ value.toPort }}""
    source_address_prefix      = "{% for range in value.cidr %}"{{ range }}"{% endfor %}"
    destination_address_prefix = "{% for range in value.cidr %}"{{ range }}"{% endfor %}"
  }
  {%- endif %}{% endif %}{% endfor %}
  tags = {
    environment = "Production"
  }
}
