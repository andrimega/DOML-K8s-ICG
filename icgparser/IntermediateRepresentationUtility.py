import logging

from icgparser.ModelResourcesUtilities import ModelResources, ModelResourcesUtilities, get_ir_key_name


def find_objects(object_name: ModelResources, intermediate_representation):
    logging.info(f"Searching for {object_name.name} in intermediate representation")
    ir_step_name = get_ir_key_name(ModelResources.STEPS)
    steps = intermediate_representation[ir_step_name]
    object_ir_name = get_ir_key_name(object_name)
    for step in steps:
        if step:
            data = step[get_ir_key_name(ModelResources.DATA)]
            if object_ir_name in data.keys():
                return data[object_ir_name]
    return []


def add_step(step, intermediate_representation, step_number):
    logging.info("Adding step into intermediate representation")
    model_resource_class = ModelResourcesUtilities()
    steps = intermediate_representation[model_resource_class.get_ir_key_name_from_model_resource(ModelResources.STEPS)]
    if step_number:
        steps.insert(step_number, step)
    else:
        steps.append(step)
    return intermediate_representation


def force_add_resources_name(to_resource, from_resource, intermediate_representation):
    logging.info(f"force_add_resources_name of resource {from_resource} into {to_resource} ")
    sec_groups = find_objects(from_resource, intermediate_representation)
    sec_groups_names = []
    logging.info(f"Found sec_groups {sec_groups} to be added into {from_resource}")
    if sec_groups and len(sec_groups):
        for key, sg in sec_groups[0].items():
            if isinstance(sg, dict) and sg["name"]:
                sec_groups_names.append(sg["name"])
        for resource in find_objects(to_resource, intermediate_representation):
            resource["infra_sgs"] = sec_groups_names
    return intermediate_representation
