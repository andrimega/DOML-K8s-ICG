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
- hosts: DB
  become: yes

  pre_tasks:
  - name: Install MySQL
    yum: name={{ item }} update_cache=yes cache_valid_time=3600 state=present
    with_items:
    - mysql-server
    - mysql-client
    - python-setuptools
    - python-mysqldb
    - libmysqlclient-dev
    - python3-pip

  - name: Remove a symbolic link
    ansible.builtin.file: 
      path: /usr/bin/python
      state: absent

  - name: Create a symbolic link
    ansible.builtin.file: 
      src: /usr/bin/python3
      dest: /usr/bin/python
      state: link
    register: result
    retries: 3
    delay: 5
    until: result is not failed

  - name: Create a symbolic link
    ansible.builtin.file: 
      src: /usr/bin/pip3
      dest: /usr/bin/pip
      state: link
    register: result
    retries: 3
    delay: 5
    until: result is not failed
      
  - name: Install Python packages
    pip: "name={{ item }} state=present"
    with_items:
      - PyMySQL

  - name: edit firewall
    service:
      name: firewalld
      state: stopped
      enabled: false

  tasks:
  - name: Start the MySQL service
    service:
      name: mysql
      state: started
      enabled: true

  - name: Creation mysql file configuration
    file:
      path: "/root/.my.cnf"
      state: touch

  - name: Editing configuration file
    replace:
      path: /etc/mysql/mysql.conf.d/mysqld.cnf
      regexp: '(.*bind-addres.*)'
      replace: '#\1'

  - name: Restart MySQL
    service: name=mysql state=restarted

  - name: Ensure MySQL started
    service:
      name: mysql
      state: started

  - name: update mysql password for application account
    mysql_user:
      name: "{{ db_user }}"
      host: "%"
      password: "{{ db_password }}"
      state: present
      login_user: root
      login_password: test
      check_implicit_admin: yes
      priv: "*.*:ALL,GRANT"

  - name: Add the application database
    mysql_db: 
      name: "{{ db_name }}"
      state: present

  - name: Restart MySQL
    service: name=mysql state=restarted
