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
#		PIACERE ICG Parser
#-------------------------------------------------------------------------
#
#       This module has been tested with Python v3.7.4
#       To use it you must first install PyEcore
#           $ pip install pyecore
#
#       Usage: python icgparser.py [-h] [-d dir] [-v] [--single] model
#           -h          prints usage
#           -d dir      loads metamodel from <dir>
#           --single / --single_mmodel   use the single (non-split) metamodel
#           model       the input model to be translated into the ICG intermediate representation
# -------------------------------------------------------------------------
import logging
import re
from icgparser import DomlParserUtilities, IntermediateRepresentationUtility
from icgparser.DomlParserUtilities import get_reference_list_if_exists, get_resources_from_concrete_layer, \
        get_infrastructure_element_from, get_external_references, remove_from_navigated_references, \
        remove_from_navigated_references_all_refs_under, save_references_info, update_missing_parsed_resources
from icgparser.ModelResourcesUtilities import ModelResourcesUtilities, ModelResources
from plugin.PluginUtility import find_external_plugins_name, find_resources_names_for_plugin

OUTPUT_BASE_DIR_PATH = "output_files_generated/"
doml_layers = {
    "active_infrastructure_layer": "activeInfrastructure",
    "infrastructure_layer": "infrastructure",
}


def to_camel_case(content):
    return content[0].lower() + content[1:]


def include_missing_objects_from_infrastructure_layer(to_step):
    missing_objects = dict.copy(DomlParserUtilities.retrieve_missing_parsed_resources())
    logging.info(f"Found {len(missing_objects)} missing infra objects.")
    for obj_name, obj in missing_objects.items():
        logging.info(f"Adding {obj_name} infra object")
        infra_object_representation = {}
        infra_object_representation = DomlParserUtilities.save_attributes(obj["resource"], infra_object_representation,
                                                                          skip_component_name=True)
        infra_object_representation = DomlParserUtilities.save_inner_components(obj["resource"],
                                                                                infra_object_representation)
        infra_object_representation = DomlParserUtilities.add_infrastructure_information(obj["resource"],
                                                                                         infra_object_representation)
        if "SecurityGroup" in str(type(obj["reference"])):
            ir_key_name = "securityGroup"
        else:
            ir_key_name = to_camel_case(obj["reference"].eType.name)
        if ir_key_name in to_step["data"].keys():
            to_step["data"][ir_key_name].append(infra_object_representation)
        else:
            to_step["data"][ir_key_name] = [infra_object_representation]
    return to_step


def include_infra_object_from_concrete_layer(provider, infra_object_step):
    logging.info(f'Adding objects from concrete layer for provider {provider.name}')
    for ref in provider.eClass.eReferences:
        provider_object_list = get_reference_list_if_exists(provider, ref)
        if provider_object_list:
            logging.info(
                f'Found list of object {len(provider_object_list)} "{provider_object_list}" in "{provider.name}"')
            object_list_representation = []
            for object in provider_object_list:
                object_representation = save_object_from_concrete_layer(object)
                object_list_representation.append(object_representation)
            infra_object_step["data"][ref.name] = object_list_representation
    return infra_object_step

def save_object_from_concrete_layer(object):
    logging.info(f"Parsing object {object.name}")
    object_representation = {}
    object_representation = DomlParserUtilities.save_annotations(object, object_representation)
    object_representation = DomlParserUtilities.save_attributes(object, object_representation)
    object_representation = DomlParserUtilities.save_references_link(object, object_representation)
    object_representation = DomlParserUtilities.save_concrete_references_info(object, object_representation)
    if DomlParserUtilities.hasMaps(object):
            object_representation = DomlParserUtilities.add_infrastructure_information(object.maps,
                                                                                       object_representation)
    return object_representation


def include_provide_info_from_concrete_layer(provider, infra_object_step):
    logging.info(f'Adding provider info from concrete layer for provider {provider.name}')
    provider_info = DomlParserUtilities.save_annotations(provider, {})
    provider_info["provider_name"] = provider.name
    infra_object_step["data"]["provider_info"] = [provider_info]
    return infra_object_step


def parse_infrastructural_objects(doml_model):
    infra_object_step = {"programming_language": "terraform"}  ## TODO refactoring: generalize
    concretization_layer = doml_model.eGet(doml_layers["active_infrastructure_layer"])
    providers = concretization_layer.providers
    infa_layer = doml_model.eGet(doml_layers["infrastructure_layer"])

    for provider in providers:
        logging.info(f'Searching objects to be generates for provider "{provider.name}"')
        infra_object_step["data"] = {}  ## TODO refactoring, fix (maybe list?): generalize
        ## infra_object_step["data"]["provider"] = provider.name

        infra_object_step = include_provide_info_from_concrete_layer(provider, infra_object_step)
        infra_object_step = include_infra_object_from_concrete_layer(provider, infra_object_step)
        try:
            infra_sec_groups = infa_layer.securityGroups
            for infra_sec_group in infra_sec_groups:
                logging.info(f'Found security group name "{infra_sec_group.name}"')
                update_missing_parsed_resources(infra_sec_group, reference=infra_sec_group, is_to_be_parsed=True)
        except:
            logging.info(f'No security group found')
        infra_object_step = include_missing_objects_from_infrastructure_layer(infra_object_step)
    return infra_object_step

def parse_k8s_deployment(deployment, infra_object_step):
    # prepare ds
    application_object_step = {"programming_language": "kubernetes", "data": {}}
    # extract component name
    application_resource = deployment.eGet("component")
    deployment_component_name = application_resource.eGet("name")
    logging.info(f'Parsing kubernetes deployment for component {deployment_component_name}')
    object_representation = {}

    # assign name
    object_representation['name'] = deployment_component_name
    # extract and assign image and ports
    image = deployment.eGet("image")
    ports = image.eGet("exposedPort")
    port_list = []
    for port in list(ports):
         port_list.append(DomlParserUtilities.save_attributes(port,{}))
    object_representation['image'] = DomlParserUtilities.save_attributes(image, {})
    object_representation['image']['ports'] = port_list
    
    # extract and assign replicas and namespace
    object_representation['replicas'] = deployment.eGet('replicas')
    object_representation['namespace'] = deployment.eGet('namespace')

    # extract and assign autoscaler
    object_representation['autoscaler'] = DomlParserUtilities.save_attributes(deployment.eGet("autoscaler"), {})

    # fill ds
    application_object_step["data"] = {"KubernetesDeployment" : object_representation}
    application_object_step["step_name"] = deployment_component_name
    application_object_step["step_type"] = "component"

    return application_object_step

def parse_k8s_ext_deployment(deployment, infra_object_step):
    application_object_step = {"programming_language": "kubernetes", "data": {}}
    deployment_component_name = "prova_depl"# deployment.component.name
    deployment_component_type = "appl_type" #deployment.component.eClass.name
    logging.info(f'Parsing deployment for component {deployment_component_name} of type {deployment_component_type}')
    object_representation = {}

    application_resource = deployment.eGet("component")
    object_representation['component'] = DomlParserUtilities.save_attributes(application_resource, {})
    object_representation['url'] = deployment.eGet("url")

    application_object_step["data"] = {"KubernetesDeployment" : object_representation}
    application_object_step["step_name"] = deployment_component_name
    application_object_step["step_type"] = deployment_component_type

    return application_object_step

def parse_application_layer(deployment, infra_object_step):
    ## TODO moved to create_intermediate_representation; to be checked
    # logging.info("DOML parsing: getting active configuration")
    # active_configuration = doml_model.activeConfiguration
    # if not active_configuration:
    #     logging.info("No application layer found")
    # else:
    #     application_object_step = {"programming_language": "ansible", "data": {}}

    application_object_step = {"programming_language": "ansible", "data": {}}
    deployment_component_name = deployment.component.name
    deployment_component_type = deployment.component.eClass.name
    logging.info(f'Parsing deployment for component {deployment_component_name} of type {deployment_component_type}')
    object_representation = {}

    application_resource = deployment.eGet("component")

    if deployment_component_type == "SoftwareComponent" or deployment_component_type == "DBMS":
        vm = deployment.eGet("node")
        # Looking for VM named vm.name
        found = False
        try:
            if "autoScalingGroups" in infra_object_step.get("data").keys():
                for ag in infra_object_step.get("data").get("autoScalingGroups"):
                    ag_vm = next(v for k, v in ag.items() if k.lower().startswith('virtualmachine'))
                    if ag_vm.get("name") == vm.name:
                        ## TODO fake list, refactoring -> far diventare lista nodi? nel monitoring sono più nodi
                        object_representation["nodes"] = [ag_vm]
                        found = True
                ## Can be optimized by doing further searches only if not found?
                for infra_vm in infra_object_step.get("data").get("virtualMachine"):
                    if infra_vm.get("infra_element_name") == vm.name:
                        ## TODO fake list, refactoring -> far diventare lista nodi? nel monitoring sono più nodi
                        object_representation["nodes"] = [infra_vm]
                        found = True
            elif "group" in infra_object_step.get("data").keys():
                for ag in infra_object_step.get("data").get("group"):
                    ag_vm = next(v for k, v in ag.items() if k.lower().startswith('virtualmachine'))
                    if ag_vm.get("name") == vm.name:
                        ## TODO fake list, refactoring -> far diventare lista nodi? nel monitoring sono più nodi
                        object_representation["nodes"] = [ag_vm]
                        found = True
                for infra_vm in infra_object_step.get("data").get("vms"):
                    if infra_vm.get("infra_element_name") == vm.name:
                        ## TODO fake list, refactoring -> far diventare lista nodi? nel monitoring sono più nodi
                        object_representation["nodes"] = [infra_vm]
                        found = True
            if not found and "vms" in infra_object_step.get("data").keys():
                for infra_vm in infra_object_step.get("data").get("vms"):
                    if infra_vm.get("infra_element_name") == vm.name:
                        ## TODO fake list, refactoring -> far diventare lista nodi? nel monitoring sono più nodi
                        object_representation["nodes"] = [infra_vm]
                        found = True
            if not found and "virtualMachine" in infra_object_step.get("data").keys():
                for infra_vm in infra_object_step.get("data").get("virtualMachine"):
                    if infra_vm.get("infra_element_name") == vm.name:
                        ## TODO fake list, refactoring -> far diventare lista nodi? nel monitoring sono più nodi
                        object_representation["nodes"] = [infra_vm]
                        found = True
            if not found:
                logging.error(f"VM missing: no vm {vm.name} found for deployment {deployment_component_name}")
                        
        except Exception:
            logging.error(f"parsing error: no vm {vm.name} found for deployment {deployment_component_name}")

    elif deployment_component_type == "SaaSDBMS":
    # Include exec_env information into saas IR
        execenv = deployment.eGet("node")
    # @@@@
        for infra_execenv in infra_object_step.get("data").get("executionEnvironments"):
            if infra_execenv.get("infra_element_name") == execenv.name:
                object_representation["nodes"] = [infra_execenv]
# Further application layer component types should be handled here

    object_representation = DomlParserUtilities.save_annotations(application_resource, object_representation)
    object_representation = DomlParserUtilities.save_attributes(application_resource, object_representation)
    object_representation = DomlParserUtilities.save_references_info(application_resource, object_representation)

    application_object_step["data"][deployment_component_name] = object_representation
    application_object_step["step_name"] = deployment_component_name
    application_object_step["step_type"] = deployment_component_type

    return application_object_step


def add_external_plugin_steps(model_loaded):
    logging.info("Adding external plugin resource in intermediate representation")
    plugins_name = find_external_plugins_name()
    plugin_steps = []
    for plugin_name in plugins_name:
        object_list_representation = []
        resources_names = find_resources_names_for_plugin(plugin_name)
        for res_name in resources_names:
            resources = get_resources_from_concrete_layer(model_loaded, res_name)
            if len(list(resources)) > 0:
                plugin_object_step = {"programming_language": plugin_name, "data": {}}
                for res in resources:
                    object_representation = save_object_from_concrete_layer(res)
                    logging.info(f"Searching link to infra element for concrete resource {res_name}")
                    infra_elem = get_infrastructure_element_from(res)
                    logging.info(f"Infra element found: {infra_elem}")
                    # Remove the container generated by the current ContainerImage from the NAVIGATED_REFERENCES list
                    cont = infra_elem.generatedContainers.items[0]
                    logging.info(f"Removing {cont.name} and all its references from NAVIGATED_REFERENCES list")
                    remove_from_navigated_references(cont)
                    remove_from_navigated_references_all_refs_under(cont)
                    logging.info(f"Searching references from infra  {infra_elem.name}")
                    object_representation = save_references_info(infra_elem, object_representation, False)
                    object_list_representation.append(object_representation)
                plugin_object_step["data"][res_name] = object_list_representation
                plugin_steps.append(plugin_object_step)
    return plugin_steps


def create_intermediate_representation(model_loaded):
    model_name = model_loaded.name
    output_path = OUTPUT_BASE_DIR_PATH + model_name + "/"
    intermediate_representation_steps = []
    infra_object_step = parse_infrastructural_objects(model_loaded)
    (intermediate_representation_steps.append(infra_object_step) if infra_object_step is not None else None)
    new_plugin_steps = add_external_plugin_steps(model_loaded)
    intermediate_representation_steps.extend(new_plugin_steps)
    active_configuration = model_loaded.activeConfiguration
    # TODO Refactoring
    if not active_configuration:
        logging.info("No application layer found")
    else:
        for deployment in list(active_configuration.deployments):
            application_step = parse_application_layer(deployment, infra_object_step)
            (intermediate_representation_steps.append(application_step) if application_step is not None else None)
        for deployment in list(active_configuration.KubernetesDeployments):
            application_step = parse_k8s_deployment(deployment, infra_object_step)
            (intermediate_representation_steps.append(application_step) if application_step is not None else None)
        for deployment in list(active_configuration.ExternalKubernetesDeployments):
            application_step = parse_k8s_ext_deployment(deployment, infra_object_step)
            (intermediate_representation_steps.append(application_step) if application_step is not None else None)
    intermediate_representation = {
        "output_path": output_path,
        "steps": intermediate_representation_steps
    }
    return intermediate_representation

def get_doml_version(doml_model):
    logging.info("Searching for DOML version")
    doml_version = doml_model.version
    if not doml_version.isnumeric():
        logging.info(f"Cleaning doml version {doml_version} from letters")
        doml_version = re.sub("[^0-9.]", "", doml_version)
    logging.info(f"Found DOML version {doml_version}")
    return doml_version

def parse_model(model_path, is_multiecore_metamodel, metamodel_directory):

    rset = DomlParserUtilities.load_metamodel(metamodel_directory=metamodel_directory,
                                              is_multiecore=is_multiecore_metamodel)
    doml_model = DomlParserUtilities.load_model(model_path, rset)
    doml_version = get_doml_version(doml_model)
    logging.info(f"Setup Singleton ModelResourcesUtilities with doml version {doml_version}")
    ModelResourcesUtilities(doml_version)
    intermediate_representation = create_intermediate_representation(doml_model)
    return intermediate_representation


