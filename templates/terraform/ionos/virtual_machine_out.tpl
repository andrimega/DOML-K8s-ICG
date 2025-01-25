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

output "instance_server_password_{{ infra_element_name }}" {
  value = random_password.server_image_password.result
}

output "instance_server_public_ip_{{ infra_element_name }}" {
  value = ionoscloud_ipblock.public_ip_{{ infra_element_name }}.ips[0]
}

output "ip_address" {
  value = ionoscloud_ipblock.public_ip_{{ infra_element_name }}.ips[0]
}