# pma playbook

This is an ansible playbook that install telegraf and cofigure to the needs of the performance monitoring component of piacere

## How to use

This playbook is automatically embeeded as iac by yhe ICG, the iac is then run by the IEM 


## How to test
There are may ways to test a playbook here we document the procedure followed in our case.
* Obtain a ssh docker image of some platform
* instantiate the ssh docker
* install the playbook requirements
* launch the playbook against it

i.e. Providing we have already an ssh docker image ... i.e. ubuntu-ssh https://git.code.tecnalia.com/smartdatalab/libraries/docker/ubuntu-ssh.git

```
docker rm -f ubuntu-ssh
docker network rm -f ubuntu-ssh
docker network create --driver=bridge --subnet=10.0.55.0/24 --driver=bridge ubuntu-ssh
docker run -d --name ubuntu-ssh --network ubuntu-ssh --ip 10.0.55.5 --env PUB_SSH_CERT_0="$(cat ~/.ssh/id_rsa.pub)" ubuntu-ssh
./ansible/playbooks/pma/install_playbook_requirements.sh 
./ansible/playbooks/pma/run-playbook.sh '{"pma_deployment_id": "123e4567-e89b-12d3-a456-426614174001", "pma_influxdb_bucket": "bucket", "pma_influxdb_token": "piacerePassword", "pma_influxdb_org": "piacere", "pma_influxdb_addr": "https://influxdb.pm.ci.piacere.digital.tecnalia.dev" }'
ssh -o StrictHostKeyChecking=no root@10.0.55.5 service telegraf status
```

the output shoud be that the "telegraf Process is running `[[ OK ]]"

## Notes
