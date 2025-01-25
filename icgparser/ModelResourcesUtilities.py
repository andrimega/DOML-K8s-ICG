import logging
from enum import Enum

class ModelResources(Enum):
    STEP_NAME = 1,
    STEPS = 2,
    DATA = 3,
    LANGUAGE = 4,
    VIRTUAL_MACHINES = 5,
    NETWORKS = 6,
    SECURITY_GROUPS = 7,
    AUTOSCALING_GROUPS = 8,
    STEP_TYPE = 9,

def from_model_resources_to_ir_names_version1(model_resource: ModelResources):
    switcher = {
        1: "step_name",
        2: "steps",
        3: "data",
        4: "programming_language",
        5: "vms",
        6: "networks",
        7: "computingGroup",
        8: "group",
        9: "step_type"
    }
    if model_resource.value[0]:
        resource_number = model_resource.value[0]
    else:
        resource_number = model_resource.value
    return switcher.get(resource_number, None)


def from_model_resources_to_ir_names_version2(model_resource: ModelResources):
    switcher = {
        1: "step_name",
        2: "steps",
        3: "data",
        4: "programming_language",
        5: "vms",
        6: "networks",
        7: "securityGroup",
        8: "autoScalingGroups",
        9: "step_type"
    }
    if model_resource.value[0]:
        resource_number = model_resource.value[0]
    else:
        resource_number = model_resource.value
    return switcher.get(resource_number, None)

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class ModelResourcesUtilities:
    doml_version = "2"

    def __init__(self, doml_version):
        logging.info(f"ModelResourcesUtilities setting doml version to {doml_version}")
        self.doml_version = doml_version

    def convert_doml_version_into_integer(self):
        return float(self.doml_version)

    def get_ir_key_name_from_model_resource(self, model_resource: ModelResources):
        #doml_version_converted = self.convert_doml_version_into_integer()
        logging.info(f"Found doml version {self.doml_version}")
        switcher = {
            "1": from_model_resources_to_ir_names_version1(model_resource),
            "2": from_model_resources_to_ir_names_version2(model_resource),
            "2.0": from_model_resources_to_ir_names_version2(model_resource),
            "2.2": from_model_resources_to_ir_names_version2(model_resource),
            "2.2.2": from_model_resources_to_ir_names_version2(model_resource),
            "2.3": from_model_resources_to_ir_names_version2(model_resource),
            "3.0": from_model_resources_to_ir_names_version2(model_resource),
            "3.1": from_model_resources_to_ir_names_version2(model_resource),
        }
        return switcher.get(self.doml_version, from_model_resources_to_ir_names_version2(model_resource))

    def set_doml_version(self, doml_version):
        self.doml_version = doml_version

def get_ir_key_name(model_resource: ModelResources):
    model_resource_utilities = ModelResourcesUtilities()
    return model_resource_utilities.get_ir_key_name_from_model_resource(model_resource)
