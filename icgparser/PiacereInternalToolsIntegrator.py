import logging
import os
from distutils.dir_util import copy_tree
from icgparser import IntermediateRepresentationUtility
from icgparser.ModelResourcesUtilities import ModelResources


def create_piacere_agents_ansible_step(piacere_component_name, intermediate_representation):
    logging.info(f"Adding info for {piacere_component_name} step")
    step_name = piacere_component_name + "_monitoring"
    vms = IntermediateRepresentationUtility.find_objects(ModelResources.VIRTUAL_MACHINES,
                                                         intermediate_representation)
    autoscaling_group_vms = IntermediateRepresentationUtility.find_objects(ModelResources.AUTOSCALING_GROUPS,
                                                                           intermediate_representation)
    intermediate_repr_step = None
    if vms or autoscaling_group_vms:
        intermediate_repr_step = {"programming_language": "ansible",
                                  "step_name": step_name,
                                  "step_type": "SoftwareComponent",
                                  "data": {step_name: {"name": step_name}}}
        intermediate_repr_step["data"][step_name]["nodes"] = []
        if vms:
            intermediate_repr_step["data"][step_name]["nodes"] += vms
        if autoscaling_group_vms:
            for ag in autoscaling_group_vms:
                vms = []
                vm = next(v for k, v in ag.items() if k.lower().startswith('virtualmachine'))
                vms.append(vm)
            intermediate_repr_step["data"][step_name]["nodes"] += vms

    logging.info(f"{step_name} step: {intermediate_repr_step}")
    return intermediate_repr_step


def extract_info_for_monitoring_agents(intermediate_representation):
    logging.info("Adding info for performance step")
    monitoring_object_step = create_piacere_agents_ansible_step("performance", intermediate_representation)
    return monitoring_object_step


def extract_infor_for_security_agents(intermediate_representation):
    logging.info("Adding info for security step")
    security_object_step = create_piacere_agents_ansible_step("security", intermediate_representation)
    return security_object_step


def extract_info_for_self_healing(intermediate_representation):
    logging.info("Adding info for self healing step")
    self_healing_object_step = create_piacere_agents_ansible_step("self_healing", intermediate_representation)
    return self_healing_object_step


def add_internal_tool_information(intermediate_representation):
    performance_monitoring_directory_path = "templates/ansible/cross-platform/performance_monitoring"
    security_monitoring_directory_path = "templates/ansible/cross-platform/security_monitoring"
    if not os.listdir(performance_monitoring_directory_path) or not os.listdir(security_monitoring_directory_path):
        logging.warning(f"add_internal_tool_information: {performance_monitoring_directory_path} "
                        f"or {security_monitoring_directory_path} is empty.")
        return intermediate_representation
    self_healing_step = extract_info_for_self_healing(intermediate_representation)
    monitoring_step = extract_info_for_monitoring_agents(intermediate_representation)
    security_step = extract_infor_for_security_agents(intermediate_representation)
    intermediate_representation_with_monitoring = IntermediateRepresentationUtility.add_step(monitoring_step,
                                                                                             intermediate_representation,
                                                                                             1)
    intermediate_representation_with_security_monitoring = IntermediateRepresentationUtility \
        .add_step(security_step, intermediate_representation_with_monitoring, 2)
    intermediate_representation_with_self_healing = IntermediateRepresentationUtility \
        .add_step(self_healing_step, intermediate_representation_with_security_monitoring, 3)
    return intermediate_representation_with_self_healing


def add_files_for_monitoring_agents(template_generated_folder_path):
    monitoring_folder_path = template_generated_folder_path + "performance_monitoring"
    if not os.path.exists(monitoring_folder_path):
        os.makedirs(monitoring_folder_path)
    logging.info(f"Adding monitoring agents folder in {monitoring_folder_path}")
    monitoring_folder = "templates/ansible/cross-platform/performance_monitoring"
    if not os.path.exists(monitoring_folder):
        os.makedirs(monitoring_folder)
    copy_tree("templates/ansible/cross-platform/performance_monitoring", monitoring_folder_path)


def add_files_for_security_agents(template_generated_folder_path):
    security_folder_path = template_generated_folder_path + "security_monitoring"
    if not os.path.exists(security_folder_path):
        os.makedirs(security_folder_path)
    logging.info(f"Adding monitoring agents folder in {security_folder_path}")
    security_folder = "templates/ansible/cross-platform/security_monitoring"
    if not os.path.exists(security_folder):
        os.makedirs(security_folder)
    copy_tree("templates/ansible/cross-platform/security_monitoring", security_folder_path)


def add_files_for_piacere_internal_tools(template_generated_folder_path):
    add_files_for_monitoring_agents(template_generated_folder_path)
    add_files_for_security_agents(template_generated_folder_path)
