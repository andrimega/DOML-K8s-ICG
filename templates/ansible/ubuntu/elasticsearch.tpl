---

- name: Elasticsearch with custom configuration
  hosts: servers_for_elasticsearch
  roles:
    - role: elastic.elasticsearch
  vars:
    es_data_dirs:
      - "/opt/elasticsearch/data"
    es_log_dir: "/opt/elasticsearch/logs"
    es_config:
      node.name: "node1"
      cluster.name: "custom-cluster"
      discovery.seed_hosts: "localhost:9301"
      http.port: 9201
      transport.port: 9301
      node.data: false
      node.master: true
      bootstrap.memory_lock: true
    es_heap_size: 1g
    es_api_port: 9201