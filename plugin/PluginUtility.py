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
# -------------------------------------------------------------------------
import logging

from plugin import TemplateUtils
from utility import PropertiesReaderUtility

plugin_properties_file_name = "external-plugins.properties"
plugin_properties_main_section = "plugins"


def createExecutionFileInstructions(iac_language, key, data, file_key_name):
    template_path = TemplateUtils.find_template_path(iac_language, key, file_key_name)
    template = TemplateUtils.read_template(template_path)
    template_path_edited = TemplateUtils.edit_template(template, data)
    return template_path_edited


def find_resources_names_for_plugin(plugin_name):
    logging.info(f"Searching for resources name for plugin {plugin_name}")
    resources = PropertiesReaderUtility.get_items_from_key(plugin_properties_file_name,
                                                           plugin_properties_main_section, plugin_name)
    logging.info(f"Founded resources: {resources}")
    return resources


def find_external_plugins_name():
    logging.info("Searching for external plugins")
    plugins_name = PropertiesReaderUtility.get_key_from_properties(plugin_properties_file_name,
                                                                   plugin_properties_main_section)
    logging.info(f"Founded plugins: {plugins_name}")
    return plugins_name
