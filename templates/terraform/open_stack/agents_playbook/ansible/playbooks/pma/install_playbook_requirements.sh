#!/bin/bash
set -e

SCRIPT_DIR=$(dirname "$0")

# to avoid the being run in a world writable directory we explicitly assign the ANSIBLE_CONFIG variable 
if [[ -f ./ansible.cfg ]]
then
    export ANSIBLE_CONFIG=./ansible.cfg
else 
    if [[ -f $SCRIPT_DIR/ansible.cfg ]]
    then
        export ANSIBLE_CONFIG=$SCRIPT_DIR/ansible.cfg
    fi
fi

if [[ -z "$ANSIBLE_CONFIG" ]]
then 
    echo ANSIBLE_CONFIG to assigned using default https://docs.ansible.com/ansible/latest/reference_appendices/config.html
else 
    echo ANSIBLE_CONFIG=$ANSIBLE_CONFIG
fi

if [[ -z "$1" ]]
then 
    # echo without params 
    echo ansible-playbook $SCRIPT_DIR/site_requirements.yaml
    ansible-playbook $SCRIPT_DIR/site_requirements.yaml
else 
    # echo with params
    echo ansible-playbook $SCRIPT_DIR/site_requirements.yaml --extra-vars "$1"
    ansible-playbook $SCRIPT_DIR/site_requirements.yaml --extra-vars "$1"
fi
