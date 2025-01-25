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

output "instance_server_public_key_{{ credentials }}_{{ infra_element_name }}" {
  value = aws_key_pair.{{ credentials }}.public_key
}

output "instance_server_public_ip_{{ infra_element_name }}" {
  value = aws_instance.{{infra_element_name}}.public_ip
}

output "instance_public_dns_{{ infra_element_name }}" {
  value = aws_instance.{{infra_element_name}}.public_dns
}

output "instance_server_private_key_{{ credentials }}_{{ infra_element_name }}" {
  value = nonsensitive(tls_private_key.example.private_key_openssh)
}