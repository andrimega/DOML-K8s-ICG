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
  become: yes

  pre_tasks:
    - name: "Install packages"
      yum: "name={{ item }} state=present"
      with_items:
        - postgresql10
        - postgresql10-server
        - postgresql10-contrib
        - postgresql10-libs
        - python3
        - python3-pip

    - name: "Install Python packages"
      pip: "name={{ item }}  state=present"
      with_items:
        - psycopg2-binary

  tasks:
 
    - name: "Start and enable services"
      service: "name={{ item }} state=started enabled=yes"
      with_items:
        - postgresql

    - name: "Create app database"
      postgresql_db:
        state: present
        name: "{{ db_name }}"
      become: yes
      become_user: postgres

    - name: "Create db user"
      postgresql_user:
        state: present
        name: "{{ db_user }}"
        password: "{{ db_password }}"
      become: yes
      become_user: postgres

    - name: "Grant db user access to app db"
      postgresql_privs:
        type: database
        database: "{{ db_name }}"
        roles: "{{ db_user }}"
        grant_option: no
        privs: all
      become: yes
      become_user: postgres

    - name: "Allow md5 connection for the db user"
      postgresql_pg_hba:
        dest: "/etc/postgresql/10/main/pg_hba.conf"
        contype: host
        databases: all
        method: md5
        users: "{{ db_user }}"
        create: true
      become: yes
      become_user: postgres
      notify: restart postgresql