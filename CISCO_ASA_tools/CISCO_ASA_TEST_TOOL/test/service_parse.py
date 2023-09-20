import os
import glob
import pdb
import textfsm
import re
from pprint import pprint

# Configuration file path(s)
PORT_LIST = {
    "aol": 5190, "bgp": 179, "biff": 512, "bootpc": 68, "bootps": 67,
    "chargen": 19, "cifs": 3020, "citrix-ica": 1494, "cmd": 514, "ctiqbe": 2748,
    "daytime": 13, "discard": 9, "dnsix": 195, "domain": 53, "echo": 7,
    "exec": 512, "finger": 79, "ftp": 21, "ftp-data": 20, "gopher": 70,
    "h323": 1720, "hostname": 101, "http": 80, "https": 443, "ident": 113,
    "imap4": 143, "irc": 194, "isakmp": 500, "kerberos": 750, "klogin": 543,
    "kshell": 544, "ldap": 389, "ldaps": 636, "login": 513, "lotusnotes": 1352,
    "lpd": 515, "mobile-ip": 434, "nameserver": 42, "netbios-dgm": 138,
    "netbios-ns": 137, "netbios-ssn": 139, "nfs": 2049, "nntp": 119, "ntp": 123,
    "pcanywhere-data": 5631, "pcanywhere-status": 5632, "pim-auto-rp": 496,
    "pop2": 109, "pop3": 110, "pptp": 1723, "radius": 1645, "radius-acct": 1646,
    "rip": 520, "rsh": 514, "rtsp": 554, "secureid-udp": 5510, "sip": 5060,
    "smtp": 25, "snmp": 161, "snmptrap": 162, "sqlnet": 1521, "ssh": 22,
    "sunrpc": 111, "syslog": 514, "tacacs": 49, "talk": 517, "Telnet": 23,
    "tftp": 69, "time": 37, "uucp": 540, "vxlan": 4789, "who": 513,
    "whois": 43, "www": 80, "xdmcp": 177
}

file_paths = glob.glob("config.txt")

# Read the configuration file(s)
with open("config.txt") as config_file:
    config_data = config_file.read()

# Define paths to TextFSM templates
srv_obj_template = "./template/object/object_service.textfsm"
srv_grp_template = "./template/object_group/object-group_service.textfsm"

# Initialize dictionaries to store object services and service groups
srv = {"obj": {}, "grp": {}}


def port_change(port):
    return str(PORT_LIST.get(port, port))

# Function to parse and store data in dictionaries
def parse_and_store_data(template_path, target_dict, config_data):
    with open(template_path) as template_file:
        fsm = textfsm.TextFSM(template_file)
        parsed_data = [dict(zip(fsm.header, item)) for item in fsm.ParseText(config_data)]
        for entry in parsed_data:
            name = entry["NAME"]
            if name not in target_dict:
                target_dict[name] = []
            target_dict[name].append(entry)

def update_group_members(srv):
    for name, values in srv["grp"].items():
        updated_values = []
        for value in values:
            if value["TYPE"] == "group" and value["GRP_OBJECT"] in srv["grp"]:
                values.extend(srv["grp"][value["GRP_OBJECT"]])
            else:
                updated_values.append(value)
        srv["grp"][name] = updated_values

# Function to process and format service data
def process_service_data(data):
    protocol = data["PROTOCOL"] if data["PROTOCOL"] else "any"

    if data["DST_PORT"]:
        dst_ope = "eq"
        dst_port = port_change(data["DST_PORT"])
    elif data["DST_PORT_RANGE_START"] and data["DST_PORT_RANGE_END"]:
        dst_ope = "range"
        dst_port = f"{port_change(data['DST_PORT_RANGE_START'])}-{port_change(data['DST_PORT_RANGE_END'])}"
    elif data["DST_PORT_LESS_THAN"]:
        dst_ope = "lt"
        dst_port = port_change(data["DST_PORT_LESS_THAN"])
    elif data["DST_PORT_GREATER_THAN"]:
        dst_ope = "gt"
        dst_port = port_change(data["DST_PORT_GREATER_THAN"])
    elif data.get("PORT_OBJECT", ""):
        dst_ope = "eq"
        dst_port = port_change(data["PORT_OBJECT"])
    elif data.get("PORT_OBJECT_START", "") and data.get("PORT_OBJECT_END", ""):
        dst_ope = "range"
        dst_port = f"{port_change(data['PORT_OBJECT_START'])}-{port_change(data['PORT_OBJECT_END'])}"
    else:
        dst_ope = "any"
        dst_port = "any"

    if data["SRC_PORT"]:
        src_ope = "eq"
        src_port =port_change( data["SRC_PORT"])
    elif data["SRC_PORT_RANGE_START"] and data["SRC_PORT_RANGE_END"]:
        src_ope = "range"
        src_port = f"{port_change(data['SRC_PORT_RANGE_START'])}-{port_change(data['SRC_PORT_RANGE_END'])}"
    elif data["SRC_PORT_LESS_THAN"]:
        src_ope = "lt"
        src_port = port_change(data["SRC_PORT_LESS_THAN"])
    elif data["SRC_PORT_GREATER_THAN"]:
        src_ope = "gt"
        src_port = port_change(data["SRC_PORT_GREATER_THAN"])
    elif data.get("PORT_OBJECT", ""):
        src_ope = "eq"
        src_port = port_change(data["PORT_OBJECT"])
    elif data.get("PORT_OBJECT_START", "") and data.get("PORT_OBJECT_END", ""):
        src_ope = "range"
        src_port = f"{port_change(data['PORT_OBJECT_START'])}-{port_change(data['PORT_OBJECT_END'])}"
    else:
        src_ope = "any"
        src_port = "any"

    return {
        "protocol": protocol,
        "dst_ope": dst_ope,
        "dst_port": dst_port,
        "src_ope": src_ope,
        "src_port": src_port,
    }

def protocol_judge(target_protocol, reference_protocol):
    if reference_protocol == "any" or reference_protocol == "ip":
        return True
    elif reference_protocol == target_protocol:
        return True
    elif reference_protocol == "tcp-udp" and (target_protocol == "tcp" or target_protocol == "udp" or target_protocol == "tcp-udp"):
        return True
    else:
        return False

def port_judge(target_port, reference_port, reference_ope):
    # ポートが "any" である場合は常に True を返す
    if reference_port == "any":
        return True

    # ポート比較の条件分岐
    if reference_ope == "eq" or reference_ope == "any":
        return int(reference_port) == int(target_port)
    elif reference_ope == "gt":
        return int(reference_port) <= int(target_port)
    elif reference_ope == "lt":
        return int(reference_port) >= int(target_port)
    elif reference_ope == "range":
        # レンジの場合、ポート範囲を解析して比較
        port_start, port_end = map(int, reference_port.split("-"))
        return port_start <= int(target_port) <= port_end

    # どの条件にも当てはまらない場合は False を返す
    return False

def srv_judge(target_protocol, target_port, srv):
    return protocol_judge(target_protocol, srv["protocol"]) and port_judge(target_port, srv["src_port"], srv["src_ope"]) and port_judge(target_port, srv["dst_port"], srv["dst_ope"])

def srvs_judge(target_protocol, target_port, srvs):
    flag = False
    for srv in srvs:
        flag = flag or srv_judge(target_protocol, target_port, srv)
    return flag

def srvs_multi_judge(target_ports_protocols, srvs):
    flag = True
    for target_port_protocol in target_ports_protocols:
        target_port, target_protocol = target_port_protocol.split("/")
        flag = flag and srvs_judge(target_protocol, target_port, srvs)
    return flag

def is_valid_port_protocol(input_str):
    # 正規表現パターンを使用してポート番号とプロトコルを検証
    pattern = r'^(\d{1,5}/(tcp|udp|tcp-udp|icmp))$'
    if re.match(pattern, input_str):
        return True
    else:
        return False

def is_valid_ports_protocols(input_str):
    # 正規表現パターンを使用してポート番号とプロトコルを検証
    flag = True
    for port_protocol in input_str:
        flag = flag and is_valid_port_protocol(port_protocol)
    return flag

def get_service(config=config_data):
    srv = {"obj": {}, "grp": {}}
    # オブジェクトネットワークデータを解析して格納
    # Parse and store data for service objects and groups
    parse_and_store_data(srv_obj_template, srv["obj"], config)
    parse_and_store_data(srv_grp_template, srv["grp"], config)

    # 入れ子構造の解消
    # Merge service group members if they reference other groups
    update_group_members(srv)

    # サービスデータを処理しやすいように変形する関数
    for key, values in srv["grp"].items():
        srv["grp"][key] = [process_service_data(value) for value in values]

    # Process and format object services data
    for key, values in srv["obj"].items():
        srv["obj"][key] = [process_service_data(value) for value in values]

    return srv

# Display the final parsed and formatted data
def main():
    srv = get_service()
    pprint(srv)
    for grp_name, srvs in srv["grp"].items():
        if srvs_judge("tcp", "3389", srvs):
            print(grp_name)

    for obj_name, srvs in srv["obj"].items():
        if srvs_judge("tcp", "80", srvs):
            print(obj_name)

if __name__ == "__main__":
    main()
