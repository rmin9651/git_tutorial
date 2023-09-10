import os
import glob
import pdb
import textfsm
import re
from pprint import pprint

file_paths = glob.glob("config.txt")

# Read the configuration file(s)
with open("config.txt") as config_file:
    config_data = config_file.read()

protocol_grp_template = "./template/object_group/object-group_protocol.textfsm"

def parse_and_store_data(template_path, target_dict, config_data):
    with open(template_path) as template_file:
        fsm = textfsm.TextFSM(template_file)
        parsed_data = [dict(zip(fsm.header, item)) for item in fsm.ParseText(config_data)]
        for entry in parsed_data:
            name = entry["NAME"]
            if name not in target_dict:
                target_dict[name] = []
            target_dict[name].append(entry)

def process_protocol_data(data):
    return {
        "protocol": data["PROTOCOL"],
        "dst_ope": "any",
        "dst_port": "any",
        "src_ope": "any",
        "src_port": "any",
    }
def get_protocol():
    protocol_dict = dict()
    parse_and_store_data(protocol_grp_template, protocol_dict, config_data)

    for key, values in protocol_dict.items():
        protocol_dict[key] = [process_protocol_data(value) for value in values]

    return protocol_dict

get_protocol()
