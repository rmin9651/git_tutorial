import os
import glob
import pdb
import textfsm
import protocol_parse
import network_parse
import service_parse
from pprint import pprint

file_paths = glob.glob("config.txt")

# Read the configuration file(s)
with open("config.txt") as config_file:
    config_data = config_file.read()

access_list_template = "./template/cisco_asa_show_access-list.textfsm"

service_data = service_parse.get_service()
network_data = network_parse.get_network()
protocol_data = protocol_parse.get_protocol()

def parse_and_store_data(template_path, target_dict, config_data):
    with open(template_path) as template_file:
        fsm = textfsm.TextFSM(template_file)
        parsed_data = [dict(zip(fsm.header, item)) for item in fsm.ParseText(config_data)]
        pprint(parsed_data)
        for entry in parsed_data:
            name = entry["ACL_NAME"]
            if name not in target_dict:
                target_dict[name] = []
            target_dict[name].append(entry)

def protocol_port_merge(protocol_group, port_group):
    result = list()
    for protocol in protocol_group:
        for port in port_group:
            port["protocol"] = protocol["protocol"]
            result.append(port)
    return result

def port_summary(data):
    # デフォルトの設定を初期化
    dst_ope = "any"
    dst_port = "any"

    if data["DST_PORT"]:
        # DST_PORTが存在する場合
        dst_ope = "eq"
        dst_port = service_parse.port_change(data["DST_PORT"])
    elif data["DST_PORT_RANGE_START"] and data["DST_PORT_RANGE_END"]:
        # DST_PORT_RANGE_START と DST_PORT_RANGE_END が両方とも存在する場合
        dst_ope = "range"
        dst_port = (
            f"{service_parse.port_change(data['DST_PORT_RANGE_START'])}-"
            f"{service_parse.port_change(data['DST_PORT_RANGE_END'])}"
        )
    elif data["DST_PORT_LESS_THAN"]:
        # DST_PORT_LESS_THAN が存在する場合
        dst_ope = "lt"
        dst_port = service_parse.port_change(data["DST_PORT_LESS_THAN"])
    elif data["DST_PORT_GREATER_THAN"]:
        # DST_PORT_GREATER_THAN が存在する場合
        dst_ope = "gt"
        dst_port = service_parse.port_change(data["DST_PORT_GREATER_THAN"])
    elif data["DST_PORT_GRP"]:
        # DST_PORT_GRP が存在する場合、対応するデータを返す
        return service_data["grp"][data["DST_PORT_GRP"]]

    # ポート条件を辞書のリストとして返す
    return [{"protocol": "any", "src_ope": "any", "src_port": "any", "dst_ope": dst_ope, "dst_port": dst_port}]


def process_access_list_data_service(data):
    if data["PROTOCOL"]:
        protocol_group = [{"protocol":data["PROTOCOL"], "src_ope": "any", "src_port": "any", "dst_ope": "any", "dst_port": "any"}]
        port_group = port_summary(data)
        return protocol_port_merge(protocol_group, port_group)
    elif data["SVC_OBJECT_GRP"]:
        if data["SVC_OBJECT_GRP"] in protocol_data:
            protocol_group = protocol_data[data["SVC_OBJECT_GRP"]]
            port_group = port_summary(data)
            return protocol_port_merge(protocol_group, port_group)
        elif data["SVC_OBJECT_GRP"] in service_data["grp"]:
            return service_data["grp"][data["SVC_OBJECT_GRP"]]
    elif data["SVC_OBJECT"] in service_data["obj"]:
        return service_data["obj"][data["SVC_OBJECT"]]

def process_access_list_data_network(data, src=True):
    type = ""
    ip = ""

    if src:
        host_key = "SRC_HOST"
        network_key = "SRC_NETWORK"
        netmask_key = "SRC_NETMASK"
        object_grp_key = "SRC_OBJECT_GRP"
        object_key = "SRC_OBJECT"
        any_key = "SRC_ANY"
    else:
        host_key = "DST_HOST"
        network_key = "DST_NETWORK"
        netmask_key = "DST_NETMASK"
        object_grp_key = "DST_OBJECT_GRP"
        object_key = "DST_OBJECT"
        any_key = "DST_ANY"

    if data[host_key]:
        type = "host"
        ip = data[host_key]
    elif data[network_key]:
        type = "network"
        ip = data[network_key] + mask_or_prefix_to_prefix(data.get(netmask_key, ""))
    elif data[object_grp_key] in network_data["grp"]:
        return network_data["grp"][data[object_grp_key]]
    elif data[object_key] in network_data["obj"]:
        return network_data["obj"][data[object_key]]
    elif data[any_key]:
        type = data[any_key]
        ip = data[any_key]

    result = [{"type": type, "ip": ip}]
    return result

def get_access_list():
    access_list_data = dict()
    parse_and_store_data(access_list_template, access_list_data, config_data)
    result = {}

    for key, values in access_list_data.items():
        result[key] = []

        for value in values:
            acl_all = value["ACL_ALL"]
            action = value["ACTION"]
            srv_data = process_access_list_data_service(value)
            src_data = process_access_list_data_network(value, src=True)
            dst_data = process_access_list_data_network(value, src=False)

            entry = {
                "acl_all": acl_all,
                "action": action,
                "srv": srv_data,
                "src": src_data,
                "dst": dst_data
            }

            result[key].append(entry)

    return result
