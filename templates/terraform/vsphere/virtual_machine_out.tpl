output "instance_server_public_key_{{ credentials }}_{{ infra_element_name }}" {
  value = tls_private_key.{{ credentials }}.public_key_openssh
}

output "instance_server_private_key_{{ credentials }}_{{ infra_element_name }}" {
  value = nonsensitive(tls_private_key.{{ credentials }}.private_key_openssh)
}

output "instance_server_user_{{ infra_element_name }}" {
  value = var.username
}

output "instance_server_public_ip_{{ infra_element_name }}" {
  value = vsphere_virtual_machine.{{ infra_element_name }}.default_ip_address
}