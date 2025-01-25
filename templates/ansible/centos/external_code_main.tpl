---

- hosts: local
{%if name == "nio3" %}  vars:
{%- for node in nodes %}
    instance_server_public_ip_{{ node.infra_element_name }}: "{% raw %}{{ hostvars['127.0.0.1'].instance_server_public_ip_{% endraw %}{{ node.infra_element_name }} {% raw %}}}{% endraw %}"
{%- endfor %}
  tasks:
  - name: write hostname using jinja2
    ansible.builtin.template:
      src: ../asset/inventory.j2
      dest: ../asset/inventory
  - command: ansible-playbook -i ../asset/inventory "../asset/{{src.entry}}"
{%else %}  tasks:
  - command: ansible-playbook -i inventory "../asset/{{src.entry}}" {%- endif %}