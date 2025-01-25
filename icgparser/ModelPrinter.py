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
import sys
from pyecore.resources import ResourceSet, URI, global_registry
import pyecore.ecore as Ecore  # This gets a reference to the Ecore metamodel implementation

#-------------------------------------------------------------------------
# Utility functions to printout the loaded model
#-------------------------------------------------------------------------
from icgparser import DomlParserUtilities

def print_obj(obj, level=0):
    for x in range(level):
        print("    ", end='')
    class_name = obj.eClass.name
    if class_name == 'Property':
        print('Class: {0}\t\t{1} = {2}'.format(class_name, obj.key, obj.value))
        return False
    if class_name == 'Deployment':
        print('Class: {0}\t\tcomponent = {1}/{2} node = {3}/{4}'.format(class_name,
                                                                        obj.component.eClass.name,
                                                                        obj.component.name,
                                                                        obj.node.eClass.name,
                                                                        obj.node.name
                                                                        ))
        return False
    try:
        obj_name = obj.name
        print('Class: {0}\t\tObject: {1}'.format(class_name, obj_name))
        return True
    except Exception:
        print('Class: {0}\t\tObject: no name'.format(class_name))
        return False


def print_contents_recursive(obj, level=0):
    if print_obj(obj, level):
        for x in obj.eContents:
            print_contents_recursive(x, level+1)


def print_model(model_path, is_multiecore_metamodel, metamodel_directory):
    rset = DomlParserUtilities.load_metamodel(metamodel_directory=metamodel_directory,
                                              is_multiecore=is_multiecore_metamodel)
    doml_model = DomlParserUtilities.load_model(model_path, rset)
    logging.info("Printing model")
    print_contents_recursive(doml_model)
