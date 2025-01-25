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

import configparser
import logging
import os
from collections import OrderedDict

import jinja2
from jinja2 import Template


@jinja2.pass_context
def get_context(c):
    return c

def find_template_path(iac_language, key, resource_name):
    try:
        properties_reader = configparser.ConfigParser()
        properties_reader.read("template-location.properties")
        if not iac_language:
            template_path = properties_reader.get(key, resource_name)
        else:
            template_path = properties_reader.get(iac_language + "." + key, resource_name)
        logging.info("Chosen template at: '%s'", template_path)
        return template_path
    except configparser.NoOptionError as error:
        logging.warning("%s. Please check properties file", error)
        pass


def edit_template(template, parameters: dict, extra_parameters=None):
    logging.info(f"Starting editing template '{template}'")
    template.globals['context'] = get_context
    template.globals['callable'] = callable
    template.globals['extra_parameters'] = extra_parameters
    render = template.render(parameters)
    template_with_custom_params = "" + render + "\n"
    return template_with_custom_params


def read_template(template_path):
    logging.info("Reading template at: '%s'", template_path)
    try:
        template = Template(open(template_path, "r").read())
        return template
    except jinja2.exceptions.TemplateSyntaxError as exc:
        # TODO or error?
        logging.warning('Syntax error on template %s, %s', template_path, exc)
        pass


def write_template(template, output_path_file):
    os.makedirs(os.path.dirname(output_path_file), exist_ok=True)
    file = open(output_path_file, "w+")
    file.write(template)
    logging.info("Writing file at: '%s'", output_path_file)
    file.close()
