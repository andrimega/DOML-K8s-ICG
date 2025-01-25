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
#-------------------------------------------------------------------------
#		PIACERE ICG Main
#
#       This module has been tested with Python v3.9.7
#       To use it you must first install PyEcore, PyYAML, Jinja2
#           $ pip install pyecore~=0.12.2
#           $ pip install PyYAML==6.0
#           $ pip install Jinja2==3.0.3
#
#       Usage: python main.py [-h] [-d dir] [-v] [--single] model
#           -h          prints usage
#           -d dir      loads metamodel from <dir>
#           --single / --single_mmodel   use the single (non-split) metamodel
#           model       the input model to be translated into the ICG intermediate representation
#
#-------------------------------------------------------------------------

import logging
import sys
from fastapi import FastAPI
import api.InfrastructureTemplateController
from controller import Orchestrator
from icgparser import ModelPrinter

fast_api = FastAPI()

fast_api.include_router(api.InfrastructureTemplateController.api_router)
logging.getLogger().setLevel(logging.INFO)

# -------------------------------------------------------------------------
# Parse parameters
# -------------------------------------------------------------------------
skip_next = False
doml_directory = "./icgparser/doml/v2"
model_filename = "icgparser/doml/v2/posidonia_openstack.domlx"
load_split_model = False
output_file_name = "iac_files.tar.gz"


# get metamodel directory from command line
def param_dir(pos, list):
    global doml_directory
    global skip_next
    doml_directory = list[pos + 1]
    print(f"    doml_directory = {doml_directory} model_filename = {model_filename}")
    skip_next = True


def param_help(pos, list):
    print(f"\nUsage: {sys.argv[0]} [-h] [-d <doml_directory>] [--single] <model_filename>\n")
    sys.exit()


# indicate to load the single-file metamodel (doml.ecore) instead of the split one
def param_single(pos, list):
    global load_split_model
    print(f"--> param_single({pos},{list}")
    load_split_model = False


options = {'-d': param_dir, '-h': param_help, '--single_mmodel': param_single, '--single': param_single,
           '--output': output_file_name}
argc = len(sys.argv)
paramlist = sys.argv[1:]
for i, param in enumerate(paramlist):
    print(f"i={i} param={param} skip_next={skip_next}")
    if param in options:
        options[param](i, paramlist)
        continue
    if skip_next:
        skip_next = False
        continue
    else:
        model_filename = param

if __name__ == '__main__':
    ModelPrinter.print_model(model_path=model_filename, is_multiecore_metamodel=load_split_model,
                             metamodel_directory=doml_directory)
    compress_folder_info = Orchestrator.create_iac_from_doml_path(model_path=model_filename,
                                                                  is_multiecore_metamodel=load_split_model,
                                                                  metamodel_directory=doml_directory)

