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


def create_files(parameters, output_path):
    language = "kubernetes"
    provider_name = "deployment"

    
    yml_file = ""
    logging.info("Creating yml template for resource 'Kubernetes Deployment'")
    resource_name = 'KubernetesDeployment'

    template_path = TemplateUtils.find_template_path(language, provider_name, resource_name)
    template = TemplateUtils.read_template(template_path)
    template_filled = TemplateUtils.edit_template(template, parameters[resource_name], parameters)
    yml_file = yml_file + template_filled + "\n"

    yml_file_stored_path = output_path + "_deployment.yml"
    TemplateUtils.write_template(yml_file, yml_file_stored_path)
    logging.info("Deployment file available at: {}".format(yml_file_stored_path)) 

