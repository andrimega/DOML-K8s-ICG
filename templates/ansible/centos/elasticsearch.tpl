---

- name: Elasticsearch with custom configuration
  hosts: servers_for_elasticsearch
  roles:
    - role: elastic.elasticsearch
  vars:
    es_data_dirs:
      - "{{ es_data_dirs }}"
    es_log_dir: "{{ es_log_dir }}"
    es_config:
      node.name: "{{ node_name }}"
      cluster.name: "{{ cluster_name }}"
      discovery.seed_hosts: "{{ discovery_seed_hosts }}"
      http.port: {{ http_port }}
      transport.port: {{ transport_port }}
      node.data: false
      node.master: true
      bootstrap.memory_lock: true
    es_heap_size: 1g
    es_api_port: {{ http_port }}