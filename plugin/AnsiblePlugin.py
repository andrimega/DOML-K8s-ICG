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

from icgparser.ModelResourcesUtilities import get_ir_key_name, ModelResources
from plugin import TemplateUtils
from plugin.PluginException import PluginResourceNotFoundError


def clean_operating_system_name(operating_system):
    operating_system_lower_case = operating_system.lower()
    logging.info(f"AnsiblePlugin: extracting operating system from {operating_system}")
    if "ubuntu" in operating_system_lower_case:
        return "ubuntu"
    if "centos" in operating_system_lower_case:
        return "centos"
    ## TODO to be update with more explicit parameter
    if "ami" in operating_system_lower_case:
        return "ubuntu"
    else:
        raise PluginResourceNotFoundError(plugin_name="AnsiblePlugin", resource_name="operating system")


def find_operating_system(parameters):
    try:
        operating_system = parameters.get("nodes")[0].get("os")
        operating_system_name = clean_operating_system_name(operating_system)
        return operating_system_name
    except Exception:
        raise PluginResourceNotFoundError(plugin_name="AnsiblePlugin", resource_name="operating system")


def create_template_file(parameters, language, operating_system, template_name):
    inventory_template_path = TemplateUtils.find_template_path(language, operating_system, template_name)
    template = TemplateUtils.read_template(inventory_template_path)
    template_filled = TemplateUtils.edit_template(template, parameters)
    return template_filled


def is_external_code(resource_params):
    return resource_params.get("src")


def create_files(step, output_path):
    language = step[get_ir_key_name(ModelResources.LANGUAGE)]
    step_name = step[get_ir_key_name(ModelResources.STEP_NAME)]
    step_type = step[get_ir_key_name(ModelResources.STEP_TYPE)]
    parameters = step["data"]
    for resource_name, resource in parameters.items():
        logging.info("Creating template for resource '%s'", resource_name)
        if "SaaS" in step_type:
            # handle SaaSDBMS and other SaaS types
            operating_system = "saas"
        else:
            operating_system = find_operating_system(resource)
        # for resource_params in parameters[resource_name]:
        resource_params = parameters[resource_name]
        if is_external_code(resource_params):
            ansible_template_path = TemplateUtils.find_template_path(language, operating_system, "external_iac")
            template = TemplateUtils.read_template(ansible_template_path)
        elif "SaaS" in step_type:
            ansible_template_path = TemplateUtils.find_template_path(language, operating_system, step_type)
        else:  
            ansible_template_path = TemplateUtils.find_template_path(language, operating_system, resource_name)
        if ansible_template_path:
            ansible_output_file_path = output_path + "/".join([step_name, "main"]) + ".yml"
            inventory_output_file_path = output_path + "/".join([step_name, "inventory"]) + ".j2"
            config_output_file_path = output_path + "/".join([step_name, "config"]) + ".yaml"
            ssh_key_output_file_path = output_path + "/".join([step_name, "ssh_key.j2"])
            if is_external_code(resource_params):
                template = TemplateUtils.read_template(ansible_template_path)
            ### TODO Refactoring
            elif "," in ansible_template_path:
                ansible_template_path = ansible_template_path.split(",")
                template = TemplateUtils.read_template(ansible_template_path[0])                   
                for i in range(1, len(ansible_template_path)):
                    output_other_ansible_name_split = ansible_template_path[i].split('/')
                    output_other_ansible_name = output_other_ansible_name_split[-1].split('.')
                    other_ansible_output_file_path = output_path + "/".join([step_name, output_other_ansible_name[0]]) + ".yml"

                    other_template = TemplateUtils.read_template(ansible_template_path[i])
                    other_template_filled = TemplateUtils.edit_template(other_template, resource_params)
                    TemplateUtils.write_template(other_template_filled, other_ansible_output_file_path)
            else:
                template = TemplateUtils.read_template(ansible_template_path)

            template_filled = TemplateUtils.edit_template(template, resource_params)

            inventory_template_filled = create_template_file(resource_params, language, operating_system, "inventory")
            config_template_filled = create_template_file(resource_params, language, operating_system, "config")
            ssh_key_template_filled = create_template_file(resource_params, language, operating_system, "ssh_key")

            TemplateUtils.write_template(inventory_template_filled, inventory_output_file_path)
            TemplateUtils.write_template(template_filled, ansible_output_file_path)
            TemplateUtils.write_template(config_template_filled, config_output_file_path)
            TemplateUtils.write_template(ssh_key_template_filled, ssh_key_output_file_path)

    logging.info("File available at: {}".format(output_path))
