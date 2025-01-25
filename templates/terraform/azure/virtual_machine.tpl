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

## CREATE VM
resource "azurerm_linux_virtual_machine" "{{ name }}" { ## REQUIRED
  resource_group_name = azurerm_resource_group.rg.{{ resource_group_name }}
  ## instance details
  name                = "{{ name }}"
  location            = azurerm_resource_group.{{ resource_group_name }}.location
  size                = "{{ size }}" ## REQUIRED
  ## administrator account
  admin_username      = "{{ admin_username }}"
  admin_password      = "{{ admin_password }}" ##For Bastion Connection
  disable_password_authentication = false
  network_interface_ids = [
    azurerm_network_interface.{{ network_name }}.id
  ]

  os_disk {
    caching              = "None"
    storage_account_type = "Standard_LRS" ## REQUIRED
  }

  admin_ssh_key {
    username = "{{ ssh_user }}"
    public_key = file("${path.module}{{ ssh_key_file }}")
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "{{ image_offer }}"
    sku       = "{{ image_sku }}"
    version   = "latest"
  }
}

## VM NETWORK INTERFACE
resource "azurerm_network_interface" "{{ name ~ "_vnet_interface" }}" {
  name                = "{{ name ~ "_nic" }}"
  location            = azurerm_resource_group.{{ resource_group_name }}.location
  resource_group_name = azurerm_resource_group.{{ resource_group_name }}.name

  ip_configuration {
    name                          = "ipconfig1"
    subnet_id                     = azurerm_subnet.{{ network_name ~ "_subnet" }}.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id = azurerm_public_ip.wordpress_public_ip.id
  }
}

## PUBLIC IP
resource "azurerm_public_ip" "{{ name ~ "_public_ip" }}" {
  name = "{{ name ~ "_public_ip" }}"
  location = azurerm_resource_group.{{ resource_group_name }}.location
  resource_group_name = azurerm_resource_group.{{ resource_group_name }}.name
  allocation_method = "Dynamic" ##REQUIRED??
  sku = "Basic"
}