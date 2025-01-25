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

resource "google_compute_instance" "{{ default }}" {
  name         = "{{ name }}"
  machine_type = "{% if 'vm_flavor' in context().keys() %}{{ vm_flavor }}{% else %}{{ instance_type }}{% endif %}"
  zone         = "{% if 'vm_Zone' in context().keys() %}{{ vm_Zone }}{% else %}{{ zone }}{% endif %}"

  boot_disk {
    initialize_params {
      image = "{{ os }}" #"debian-cloud/debian-9"
    }
  }

  scratch_disk {
    interface = "SCSI"
  }

  network_interface {
    network = "default"

    access_config {
    }
  }

}