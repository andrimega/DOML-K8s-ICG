# Copyright 2022 Hewlett Packard Enterprise Development LP
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

import logging

from plugin import TemplateUtils

namespaces = {}

## creates kubernetes yaml file from ir step
def create_files(parameters, output_path):
    language = "kubernetes"
    provider_name = "deployment"
    
    yml_file = ""
    logging.info("Creating yml template for resource 'Kubernetes Deployment'")
    resource_name = 'KubernetesDeployment'

    # add namespace to namespace dict
    if namespaces.get(parameters['cluster_name'],None):
        namespaces[parameters['cluster_name']].add(parameters[resource_name]['namespace'])
    else:
        namespaces[parameters['cluster_name']] = set()
        namespaces[parameters['cluster_name']].add(parameters[resource_name]['namespace'])

    template_path = TemplateUtils.find_template_path(language, provider_name, resource_name)
    template = TemplateUtils.read_template(template_path)
    template_filled = TemplateUtils.edit_template(template, parameters[resource_name], parameters)
    yml_file = yml_file + template_filled + "\n"

    yml_file_stored_path = output_path + "_deployment.yml"
    TemplateUtils.write_template(yml_file, yml_file_stored_path)
    logging.info("Deployment file available at: {}".format(yml_file_stored_path)) 

## creates list of commands to deploy resources
def create_commands(parameters: dict, output_path: str):
    output = ''
    commands_path = output_path + "/deployments.txt"
    configure_kubectl = "aws eks update-kubeconfig --name my-cluster --region us-west-1\n"
    apply_kubectl = "kubectl apply -f "
    namespace_kubectl = "kubectl create namespace "
    # iterate over clusters
    for cluster_name,resources in parameters.items():
        # points kubectl to cluster
        output = output + configure_kubectl.replace('my-cluster',cluster_name)
        # add namespace creation
        for namespace in namespaces.get(cluster_name,None):
            if namespace != 'default':
                output = output + namespace_kubectl + namespace + '\n'
        # add resource creation
        for resource in resources:
            output = output + apply_kubectl + resource + '\n'
    with open(commands_path,'w') as out:
        out.write(output)
        


