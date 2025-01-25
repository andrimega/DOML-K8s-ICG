{# Copyright 2023 Hewlett Packard Enterprise Development LP
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
# from the first example in https://docs.ansible.com/ansible/5/collections/community/aws/rds_instance_module.html
# Note: These examples do not set authentication details, see the AWS Guide for details.
# create minimal instance in default VPC and default subnet group
- name: {{ name }}
  community.aws.rds_instance:
    # from saas_dbms oracledb
    db_instance_identifier: {{ databaseName }}
    engine: {{ engine }}
    engine_version: {{ engineVersion }}
    storage_encrypted: {{ encrypted }}
    publicly_accessible: {{ publicly_accessible }}
    # from exec_env concrete_oracledb_env
    instance_type: {{ nodes[0].instance_type }}
    storage_type: {{ nodes[0].storage_type }}
    # from exec_env oracledb_env
    # documentation says it should be integer
    allocated_storage: {{ nodes[0].size }} 
    max_allocated_storage: {{ nodes[0].maxSize }}
    region: {{ nodes[0].Location.region }}
    availability_zone: {{ nodes[0].Location.zone }}
    # Should the subnet_goup name be got from the Terraform output?
    subnet_group: {{ nodes[0].network }}
    # This is for the account to access the DB; for now we can go with the default account (oracle\oracle?)
    # username: "{{ username }}"
    # password: "{{ password }}"
