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

# we need 1 public ip
resource "ionoscloud_ipblock" "public_ip_{{ infra_element_name }}" {
  name     = "Public IP for Piacere demo"
  location = ionoscloud_datacenter.dc_for_vm.location
  size     = 1
}

# Create virtual machine
resource "ionoscloud_server" "{{ infra_element_name }}" {
  name              = "{{ name }}"
  datacenter_id     = ionoscloud_datacenter.dc_for_vm.id
  cores             = {% if 'vm_Virtual_CPU_Cores' in context().keys() %}{{ vm_Virtual_CPU_Cores }}{% else %}{{ cpu_count }}{% endif %}
  ram               = {% if 'vm_Memory' in context().keys() %}{{ vm_Memory }}{% else %}{{ memory_mb }}{% endif %}
  image_name        = "{% if 'vm_Flavor' in context().keys() %}{{ vm_Flavor }}{% else %}{{ os }}{% endif %}"
  availability_zone = "AUTO"
  ssh_key_path = [
    "./ssh_key"
  ]
  nic {
    lan             = ionoscloud_lan.lan_for_{{ infra_element_name }}.id
    dhcp            = true
    firewall_active = false
    name            = "public_nic_{{ infra_element_name }}"
    ips = [
    ionoscloud_ipblock.public_ip_{{ infra_element_name }}.ips[0]]
  }
  volume {
    # /dev/vda1
    name      = "main-hdd"
    size      = {% if 'vm_Instance_Storage' in context().keys() %}{{ vm_Instance_Storage }}{% else %}{{ storage }}{% endif %}
    disk_type = "HDD"
    user_data = base64encode(<<EOF
#!/bin/bash
apt update
apt -y install ffmpeg vlc wget iproute2

adduser vlc-user
usermod -aG sudo vlc-user

mkdir -p /srv/piacere /srv/piacere/pipes /srv/piacere/data

wget -O /srv/piacere/data/piacere.mkv "https://koofr.islonline.com/content/links/6541b213-ddc8-4d71-7369-f70642b9d73f/files/get/piacere.mkv?path=%2F"

mkfifo /srv/piacere/pipes/pipe1

tee /srv/piacere/loop-and-transcode.sh <<LAT >/dev/null
#!/usr/bin/env bash

exec ffmpeg \
    -nostdin \
    -re \
    -y \
    -fflags +genpts \
    -stream_loop -1 \
    -i "/srv/piacere/data/piacere.mkv" \
    -g 75 \
    -quality realtime \
    -speed 5 \
    -threads 4 \
    -tile-columns 4 \
    -frame-parallel 1 \
    -row-mt 1 \
    -qmin 4 \
    -qmax 48 \
    -b:v 500k \
    -c:v libvpx-vp9 \
    -an \
    -f webm \
    "/srv/piacere/pipes/pipe1"
LAT

tee /srv/piacere/http-server.sh <<HS >/dev/null
#!/usr/bin/env bash

export SUDO_UID=$(id -u vlc-user)
exec vlc-wrapper \
    -I dummy \
    /srv/piacere/pipes/pipe1 \
    --sout '#http{mux=webm, dst=:5001}' \
    --no-sout-all \
    --sout-keep
HS

chown -R vlc-user:vlc-user /srv/piacere
chmod a+x /srv/piacere/loop-and-transcode.sh /srv/piacere/http-server.sh

systemd-run \
  --unit=piacere-loop-and-transcode \
  --description="Piacere stream looper and transcoder" \
  /srv/piacere/loop-and-transcode.sh

systemd-run \
  --unit=piacere-http-server \
  --description="Piacere stream HTTP server" \
  /srv/piacere/http-server.sh
      EOF
    )
  }
}