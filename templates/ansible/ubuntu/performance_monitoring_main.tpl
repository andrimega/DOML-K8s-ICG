---
- hosts: localhost
  tasks:
    - name: print disclamer
      debug:
        msg: this can also be done with "ansible-galaxy install -r requirements"
    - name: install telegraf from galaxy
      community.general.ansible_galaxy_install:
        type: role
        requirements_file: ansible_requirements.yml

- hosts: servers_for_performance_monitoring
  pre_tasks:
    - name: Check parameters
      fail:
        msg: 'variable {{item}} not defined'
      when: item is not defined
      with_items:
        - pma_deployment_id
        - pma_influxdb_bucket
        - pma_influxdb_token
        - pma_influxdb_org
        - pma_influxdb_addr
    - name: Print parameters
      debug:
        msg: 
          - "pma_deployment_id: {{ pma_deployment_id }}"
          - "pma_influxdb_bucket: {{ pma_influxdb_bucket }}"
          - "pma_influxdb_token: {{ pma_influxdb_token }}"
          - "pma_influxdb_org: {{ pma_influxdb_org }}"
          - "pma_influxdb_addr: {{ pma_influxdb_addr }}"
    - name: Ensure gnupg package
      package:
        name: gnupg
        state: present
      become: true
  vars_files:
    - vars/main.yaml
  tasks:
    - name: Install telegraf
      ansible.builtin.include_role:
        name: dj-wasabi.telegraf
