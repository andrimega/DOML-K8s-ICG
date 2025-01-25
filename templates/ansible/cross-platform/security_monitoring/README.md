# sma-playbook

Security Monitoring Agent (Wazuh agent) deployment as a docker

## Usage - "baremetal"

### Configuration

Important variables within `vars.yml` include these:

```
---
wazuh_manager_hostname: "wazuh-manager"
wazuh_manager_port: "1514"

piacere_deployment_id: "123e4567-e89b-12d3-a456-demo-PIACERE"
```

All these variables can be overriden via environemnt. 

### Run the playbook

To run the playbook:

```
ansible-playbook main.yml -i inventory.txt
```

The Wazuh agent should be running as a process on the target infrastructure (e.g., a VM).

## Usage - Docker

To build the agent's docker image on `docker` host from the `inventory`, run this command:

```
ansible-playbook build-wazuh-agent.yml -i inventory.txt
```

You could also build the image manually and push it to some other docker registry. In this case you should change the variable for the image name within `vars.yml`.

### Running the agent and modifying Inventory file

To start the deployment locally (local docker engine), run this command:

```
ansible-playbook deploy-wazuh-docker-agent.yml -i inventory.txt
```

In order docker engine is on the other machine, change the inventory accordingly. 

### Configuration

Example of the configuration (`vars.yml`):

```
---
service_config_dir: "{{ ansible_env.HOME }}/piacere-wazuh-agent"
docker_image_build_dir: "{{ ansible_env.HOME }}/piacere-wazuh-agent/image"
wazuh_manager_hostname: "wazuh-manager"
wazuh_manager_port: "1514"

wazuh_agent_network: "security-monitoring-deployment_default"
wazuh_agent_name: "wazuh-agent-container-2"
wazuh_agent_group: "default"
wazuh_agent_config_volume: "{{ service_config_dir }}/ossec.conf:/var/ossec/etc/ossec.conf"
wazuh_agent_image_name: "wazuh-agent-image"

piacere_deployment_id: "123e4567-e89b-12d3-a456-426614174002"
```

All these variables can be overriden via environment. 

### `Build Wazuh Agent` playbook

It uses `community.docker.docker_image` module. It copies `docker-deploy` dir to the target and then it builds the agent's image with the name from the `vars.yml` on the target machine from the inventory. 

### `Deploy Wazuh Docker Agent` playbook

It uses `community.docker.docker_container` module.  The module runs the image with a name of `wazuh-agent-deploy:latest` by default (configurable within `vars.yml`), using the network `security-monitoring-deployment_default`, on the target machine. It is very important that the Wazuh Manager runs on the same network, otherwise the agent will not be able to contact the manager. `hostname` of the Agent will be set accordingly and visible in the Manager. ENV variable `WAZUH_MANAGER` sets the hostname of the Manager running on the network mentioned above. `WAZUH_AGENT_GROUP` will also to be taken into account by the Agent deployment. `ossec.conf` from the `docker-deploy` directory will be copied to the container's `/var/ossec/` directory. 

## Run the agent as a docker instance manually, not advisable

Consider this section as a backup in the case you can not use the playbooks above. 

Build the image

```
cd docker-deploy
docker build -t docker-wazuh-agent:latest .
```

Run the agent attached to network `security-monitoring-deployment_default` where Wazuh Manager should be already running.

```
docker run -d --name wazuh-agent --network=security-monitoring-deployment_default --hostname localhost -e WAZUH_MANAGER=wazuh-manager -e WAZUH_AGENT_GROUP=default -v ${PWD}/ossec.conf:/var/ossec/etc/ossec.conf docker-wazuh-agent:latest
```