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

## VIRTUAL NETWORK
resource "azurerm_virtual_network" "{{ name ~ "_vnetwork" }}" {
  name                = "{{ name }}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.{{ resource_group_name }}.location
  resource_group_name = azurerm_resource_group.{{ resource_group_name }}.name
}

## SUBNET
resource "azurerm_subnet" "{{ name ~ "_subnet" }}" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.{{ resource_group_name }}.name
  virtual_network_name = azurerm_virtual_network.{{ name ~ "_vnetwork" }}.name
  address_prefixes       = ["10.0.2.0/24"]
}