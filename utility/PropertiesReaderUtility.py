import configparser
import logging
import os


def read_properties_file(properties_file_name):
    current_folder = os.path.dirname(os.path.realpath(__file__))
    logging.info(f"Reading {properties_file_name} file from folder {current_folder}")
    config = configparser.ConfigParser()
    config.read(properties_file_name)
    return config

def get_sections(properties_file_name):
    logging.info(f"Searching section in file {properties_file_name}")
    config_parser = read_properties_file(properties_file_name)
    sections =config_parser.sections()
    logging.info(f"Founded sections {sections}")
    return sections

def get_items_from_section(properties_file_name, section):
    logging.info(f"Searching items in {properties_file_name}.{section}")
    config_parser = read_properties_file(properties_file_name)
    sections = get_sections(properties_file_name)
    for sec in sections:
        if sec == section:
            items = dict(config_parser.items(section))
            logging.info(f"Founded {items} in {properties_file_name}.{section}")
            return items
    return logging.info(f"No section {section} found in {properties_file_name}")

def get_items_from_key(properties_file_name, section, key):
    logging.info(f"Searching items in {properties_file_name}.{section}.{key}")
    items = get_items_from_section(properties_file_name, section)
    values = items.get(key)
    return values.split(",")

def get_key_from_properties(properties_file_name, section):
    logging.info(f"Searching items in {properties_file_name}.{section}")
    items = get_items_from_section(properties_file_name, section)
    return items.keys()




