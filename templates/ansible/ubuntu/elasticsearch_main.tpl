---

- hosts: localhost

  pre_tasks:
    - file:
        path:  roles
        state: absent

    - command: ansible-galaxy install elastic.elasticsearch,v7.17.0
  tasks:
    - command: ansible-playbook -i inventory elasticsearch.yml