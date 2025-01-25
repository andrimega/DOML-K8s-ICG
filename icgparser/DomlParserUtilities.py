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

from pyecore.ecore import EOrderedSet, EEnumLiteral, EcoreUtils
from pyecore.resources import ResourceSet, URI, global_registry
import pyecore.ecore as Ecore  # This gets a reference to the Ecore metamodel implementation

TO_BE_PARSED_RESOURCES = {}
METAMODEL_SECTIONS = ["doml", "commons", "application", "infrastructure", "concrete", "optimization"]
METAMODEL_DIRECTORY = "icgparser/doml"
NAVIGATED_REFERENCES = []

doml_layers = {
    "active_infrastructure_layer": "activeInfrastructure",
}

def remove_from_navigated_references(resource):
    if(resource in NAVIGATED_REFERENCES):
        NAVIGATED_REFERENCES.remove(resource)

def remove_from_navigated_references_all_refs_under(resource):
    # same way to access all references of the given object as in save_references_link()
    refs = resource.eClass.eAllReferences()
    for ref in refs:
        reference_object_list = get_reference_list_if_exists(resource, ref)
        if reference_object_list:
            for reference_object in reference_object_list:
                if(reference_object in NAVIGATED_REFERENCES):
                    NAVIGATED_REFERENCES.remove(reference_object)



def extract_value_from(ecore_object_value):
    if isinstance(ecore_object_value, EOrderedSet):
        value = list(ecore_object_value)
    elif isinstance(ecore_object_value, EEnumLiteral):
        value = ecore_object_value.name
    else:
        value = ecore_object_value
    return value

def get_infrastructure_element_from(concrete_element):
    try:
        return concrete_element.maps
    except Exception:
        logging.warning(f"No infrastructure link found for element {concrete_element.name}")
        return None


def get_reference_list_if_exists(from_object, reference):
    reference_from_object = from_object.eGet(reference.name)
    if reference_from_object and isinstance(reference_from_object, EOrderedSet) and len(reference_from_object) > 0:
        return reference_from_object
    else:
        return None

def get_references(from_object):
    refs = from_object.eClass.eAllReferences()
    return list(refs)

def get_external_references(from_object):
    try:
        return list(from_object.eClass.eReferences)
    except Exception:
        logging.warning(f"Error searching for references for object {from_object.name}")
        return None


def get_resources_from_concrete_layer(doml_model, resource_name):
    concretization_layer = get_concrete_layer(doml_model)
    providers = concretization_layer.providers
    for provider in providers:
        logging.info(f'Searching object {resource_name} in concrete layer "{concretization_layer.name}"')
        try:
            resources = provider.eGet(resource_name+"")
            logging.info(f"Found {len(list(resources))} {resource_name}")
            return resources
        except Exception:
            logging.warning(f"No resources found for {resource_name}")
            return []


def get_concrete_layer(doml_model):
    concretization_layer = doml_model.eGet(doml_layers["active_infrastructure_layer"])
    return concretization_layer

def save_annotations(from_object, to_object):
    #print(f'Saving annotation from {from_object.name}')
    if not to_object:
        to_object = {}
    try:
        for annotation in from_object.annotations:
            if "SProperty" in str(type(annotation)) or "BProperty" in str(type(annotation)) or "FProperty" in str(type(annotation)) or "IProperty" in str(type(annotation)):
                to_object[annotation.key] = annotation.value
            elif "ListProperty" in str(type(annotation)):
                list_object = {}
                for value in annotation.values:
                    list_object[value.key] = value.value
                to_object[annotation.key] = list_object
            else:
                # Don't know which case is covered here, so...
                logging.info(f"Met Annotation of type {str(type(annotation))}")
                to_object[annotation.key] = annotation.values
    except:
        logging.info(f"No Annotation in element type {str(type(from_object))}")
    return to_object

def save_attributes(from_object, to_object, skip_component_name=False):
    #print(f'Saving attributes from {from_object.name}')
    if not to_object:
        to_object = {}
    for attribute in from_object.eClass.eAllAttributes():
        if from_object.eGet(attribute.name) is not None:
            key = attribute.name
            if skip_component_name and attribute.name == "name":
                key = "infra_element_name"
                print(f'Renaming attributes {attribute.name} from {from_object.name} into {key}')
                ## TODO manage this (pay attention: error with sg!!)
            # elif attribute.name == "name":
            #     key = "concrete_element_name"
            #     print(f'Renaming attributes {attribute.name} from {from_object.name} into {key}')
            value = from_object.eGet(attribute.name)
            if isinstance(value, EOrderedSet):
                value = list(value)
            if isinstance(value, EEnumLiteral):
                value = value.name
            to_object[key] = value
    return to_object


def update_missing_parsed_list_resources(resource, reference, is_to_be_parsed):
    for attribute in resource.eClass.eAllAttributes():
        resource_name = attribute.name
        if is_to_be_parsed and not (resource_name in TO_BE_PARSED_RESOURCES):
            print(f'Adding {resource_name} as missing parsed resource')
            TO_BE_PARSED_RESOURCES[resource_name] = {"resource": resource,
                                                    "reference": reference}  ## TODO introdurre interfaccia
        elif not is_to_be_parsed and (resource_name in TO_BE_PARSED_RESOURCES):
            print(f'Removing {resource_name} to the missing parsed resource')
            del TO_BE_PARSED_RESOURCES[resource_name]
        else:
            print(f'update_missing_parsed_resources: skipping {resource_name}')

def update_missing_parsed_resources(resource, reference, is_to_be_parsed):
    resource_name = resource.name
    if is_to_be_parsed and not (resource_name in TO_BE_PARSED_RESOURCES):
        print(f'Adding {resource_name} as missing parsed resource')
        TO_BE_PARSED_RESOURCES[resource_name] = {"resource": resource,
                                                 "reference": reference}  ## TODO introdurre interfaccia
    elif not is_to_be_parsed and (resource_name in TO_BE_PARSED_RESOURCES):
        print(f'Removing {resource_name} to the missing parsed resource')
        del TO_BE_PARSED_RESOURCES[resource_name]
    else:
        print(f'update_missing_parsed_resources: skipping {resource_name}')


def save_references_info(from_object, to_object, recursive=True):
    logging.info(f"Searching references from {from_object}")
    refs = from_object.eClass.eReferences
    for ref in refs:
        if get_reference_list_if_exists(from_object, ref):
            logging.info(f'{ref.name} is a list')
            object_representation_list = []
            for reference_object in get_reference_list_if_exists(from_object, ref):
                logging.info(f'{reference_object} is the list type')
                if reference_object.name:
                    logging.info(f'Adding info for ref_link "{reference_object.name}"')
                    object_representation = {}
                    object_representation = save_annotations(reference_object, object_representation)
                    object_representation = save_attributes(reference_object, object_representation)
                    object_representation = save_references_link(reference_object, object_representation)
                    #object_representation_list.append(object_representation)
                    if(recursive):
                        save_references_info(reference_object, object_representation, False)
                    object_representation_list.append(object_representation)
            to_object[ref.name] = object_representation_list
            logging.info(f"References added: {to_object}")
        elif from_object.eGet(ref.name):
            logging.info(f'Adding object info "{ref.name}"')
            reference_object = from_object.eGet(ref.name)
            object_representation = {}
            object_representation = save_annotations(reference_object, object_representation)
            object_representation = save_attributes(reference_object, object_representation)
            object_representation = save_references_link(reference_object, object_representation)
            to_object[ref.name] = object_representation
    return to_object


def save_references_link(from_object, to_object):  ## TODO refactoring
    refs = from_object.eClass.eAllReferences()
    for ref in refs:
        reference_object_list = get_reference_list_if_exists(from_object, ref)
        if reference_object_list:
        #if get_reference_list_if_exists(from_object, ref):
            logging.info(f'{ref.name} is a list, skipping it')
            logging.info(f'{reference_object_list}')
            object_representation_list = []
            for reference_object in reference_object_list:
                object_representation = {}
                #object_representation = save_annotations(reference_object, object_representation)
                object_representation = save_attributes(reference_object, object_representation)                    
                if not reference_object in NAVIGATED_REFERENCES:
                    NAVIGATED_REFERENCES.append(reference_object)
                    if hasattr(reference_object, "name"):
                        logging.info(f'Added {reference_object.name} to NAVIGATED_REFERENCES list')
                    else:
                        logging.info(f'Added {reference_object} to NAVIGATED_REFERENCES list')
                    object_representation = save_annotations(reference_object, object_representation)
                    object_representation = save_references_link(reference_object, object_representation)
                    #save_references_info(reference_object, object_representation)
                else:
                    if hasattr(reference_object, "name"):
                        logging.info(f'Skipping {reference_object.name} as already in NAVIGATED_REFERENCES list')
                    else:
                        logging.info(f'Skipping {reference_object} as already in NAVIGATED_REFERENCES list')
                #save_references_info(reference_object, object_representation)
                object_representation_list.append(object_representation)                                
                #update_missing_parsed_list_resources(reference_object, reference=ref, is_to_be_parsed=True)
            if not ref.name in to_object:
                to_object[ref.name] = object_representation_list
            else:
                key = "infra_" + ref.name
                print(f'Renaming references key from {ref.name} into {key}')
                to_object[key] = object_representation_list
            logging.info(f"References added: {object_representation_list}")
        ## TODO trattare la lista
        elif from_object.eGet(ref.name):
            logging.info(f'Adding reference "{ref.name}" location')
            reference_object = from_object.eGet(ref.name)
            to_object[ref.name] = reference_object.name
            update_missing_parsed_resources(reference_object, reference=ref, is_to_be_parsed=True)
    return to_object

def save_concrete_references_info(from_object, to_object):
    if "refs" in dir(from_object):
        logging.info(f"Adding concrete references for object {from_object.name}")
        refs = from_object.refs
        for ref_elem in refs:
            logging.info(f"Found reference {ref_elem} for object {from_object.name}")
            inner_component = save_attributes(ref_elem, {})
            save_references_link(ref_elem, inner_component)
            to_object[ref_elem.name] = inner_component
    else:
        logging.info(f"No concrete references found for object {from_object.name}")
    return to_object

def save_inner_components(from_object, to_object):
    inner_components = from_object.eAllContents()
    for obj in inner_components:
        to_object = save_inner_component(obj, to_object)
    return to_object

def save_inner_component(component, to_object):
    if not isinstance(component, EOrderedSet):  # TODO espandere info
        logging.info("Saving inner component")
        if "Property" in str(type(component)):
            if component.key is not None:
                object_name = component.eClass.name + "_" + component.key
                to_object[object_name] = component.value
        else:
            if component.name is not None:
                object_name = component.eClass.name + "_" + component.name
            else:
                logging.warning(f'Object name not available, changing it using class name: {component.eClass.name}')
                object_name = component.eClass.name
            print(f'Saving information from object {object_name}')
            inner_component = save_attributes(component, {})
            save_references_link(component, inner_component)
            to_object[object_name] = inner_component
    return to_object


def add_infrastructure_information(infrastructure_element, to_object):
    #print(f'Infrastructure information {infrastructure_element}')
    print(f'Infrastructure information type {str(type(infrastructure_element))}')
    if not "Property" in str(type(infrastructure_element)):
        print(f'Saving infrastructure information from {infrastructure_element.name}')
        update_missing_parsed_resources(infrastructure_element, is_to_be_parsed=False, reference=None)
        save_attributes(infrastructure_element, to_object, skip_component_name=True)
        save_references_link(infrastructure_element, to_object)
        save_inner_components(infrastructure_element, to_object)
    else:
        print(f'Saving infrastructure information from {infrastructure_element.key}')
        update_missing_parsed_resources(infrastructure_element, is_to_be_parsed=False, reference=None)
        save_attributes(infrastructure_element, to_object, skip_component_name=True)
        save_references_link(infrastructure_element, to_object)
        save_inner_components(infrastructure_element, to_object)
    return to_object

def retrieve_missing_parsed_resources():
    return TO_BE_PARSED_RESOURCES


def load_metamodel(metamodel_directory=METAMODEL_DIRECTORY, is_multiecore=False):
    global_registry[Ecore.nsURI] = Ecore
    rset = ResourceSet()
    if is_multiecore:
        logging.info(f"Loading multiecore metamodel from {metamodel_directory}")
        for mm_filename in METAMODEL_SECTIONS:
            resource = rset.get_resource(URI(f"{metamodel_directory}/{mm_filename}.ecore"))
            mm_root = resource.contents[0]  # Get the root of the MetaModel (EPackage)
            rset.metamodel_registry[mm_root.nsURI] = mm_root
    else:
        logging.info(f"Loading ecore metamodel from {metamodel_directory}")
        resource = rset.get_resource(URI(f"{metamodel_directory}"))
        mm_root = resource.contents[0]  # Get the root of the MetaModel (EPackage)
        rset.metamodel_registry[mm_root.nsURI] = mm_root
        for subp in mm_root.eSubpackages:
            rset.metamodel_registry[subp.nsURI] = subp
    return rset


def load_model(model_path, rset):
    doml_model_resource = rset.get_resource(URI(model_path))
    DOML_MODEL = doml_model_resource.contents[0]
    return DOML_MODEL


def hasMaps(object):
    try:
        object.maps
        return True
    except:
        logging.info("No maps found")
        return False
