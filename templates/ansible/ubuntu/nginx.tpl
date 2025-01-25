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

---
- hosts: {{ "servers_for_" ~ name }}
  gather_facts: no
  become: yes
  tasks:
    - name: Update repositories
      apt:
        update_cache: yes

    - name: Install nginx
      package:
        name: nginx

    - name: Start nginx
      service:
        name: nginx
        enabled: yes
        state: started

    - name: Set attributes
      set_stats:
        data:
          site_config_dir: /etc/nginx/conf.d

    - name: Install sample site
      copy:
        dest: {% raw %}"{{ item }}"{%endraw%}
        content: |
          <!doctype html>
          <html lang="en">
          <head>
            <title>Hello World!</title>
          </head>
          <body>
            <h1>Sample web page</h1>
            <p>With little content ;)</p>
          </body>
          </html>
      with_items:
        - /var/www/html/index.html
        - {{ source_code }}

