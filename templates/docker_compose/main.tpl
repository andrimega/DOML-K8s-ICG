---
- hosts: {{ "servers_for_" ~ name }}
  gather_facts: no
  become: yes
  pre_tasks:
    - name: install package
      package:
        name: "docker-ce"
        state: present
    - name: install package
      package:
        name: "docker-compose-plugin"
        state: present
  tasks:
    - name: Copy over docker compose
      copy:
        src: docker_compose.yml
        dest: .
    - name: Deploy application
      docker_compose:
        definition: docker_compose.yml
