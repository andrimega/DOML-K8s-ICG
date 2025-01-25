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
from distutils.dir_util import copy_tree

from plugin import TemplateUtils, PluginUtility


def create_files(parameters, output_path):
    language = "terraform"
    provider_name = parameters["provider_info"][0]["provider_name"]

    config_file = PluginUtility.createExecutionFileInstructions(language, provider_name, parameters, "config")

    resources = parameters.keys()
    terraform_main_file = ""
    terraform_out_file = ""
    for resource_name in resources:
        logging.info("Creating output and main terraform template for resource '%s'", resource_name)

        template_for_main_path = TemplateUtils.find_template_path(language, provider_name, resource_name)
        template_for_output_path = TemplateUtils.find_template_path(language, provider_name,
                                                                    get_resource_out_path(resource_name))
        if template_for_main_path:
            for resource_params in parameters[resource_name]:
                template = TemplateUtils.read_template(template_for_main_path)
                # resource = parameters[resource_name]
                template_filled = TemplateUtils.edit_template(template, resource_params, parameters)
                terraform_main_file = terraform_main_file + template_filled + "\n"

        if template_for_output_path:
            for resource_params in parameters[resource_name]:
                template_out = TemplateUtils.read_template(template_for_output_path)
                # resource = parameters[resource_name]
                template_out_filled = TemplateUtils.edit_template(template_out, resource_params, None)
                terraform_out_file = terraform_out_file + template_out_filled + "\n"
    main_file_stored_path = output_path + "/main.tf"
    TemplateUtils.write_template(terraform_main_file, main_file_stored_path)
    output_file_stored_path = output_path + "/output.tf"
    TemplateUtils.write_template(terraform_out_file, output_file_stored_path)
    config_file_stored_path = output_path + "/config.yaml"
    TemplateUtils.write_template(config_file, config_file_stored_path)
    logging.info("Terraform main file available at: {}".format(main_file_stored_path))
    logging.info(f"Terraform output file available at {output_file_stored_path}")

## TODO spostare i template di out in una cartella?? es. cartella vms&vms_out? altrimenti come prendo nome di out?
## non è nel doml
def get_resource_out_path(resource_name):
    return resource_name + "_out"
