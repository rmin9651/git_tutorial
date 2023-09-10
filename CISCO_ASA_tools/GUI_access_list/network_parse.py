import os
import glob
import textfsm
import ipaddress
from pprint import pprint
import re

# 設定ファイルのパスを取得
file_paths = glob.glob("config.txt")

# 設定ファイルの内容を読み込む
with open("config.txt") as config_file:
    config_data = config_file.read()

# テンプレートファイルのパス
ntw_obj_template = "./template/object/object_network.textfsm"
ntw_grp_template = "./template/object_group/object-group_network.textfsm"

# オブジェクトネットワークとネットワークグループを格納する辞書を初期化
ntw = {"obj": {}, "grp": {}}

def mask_or_prefix_to_prefix(input_value):
    if '/' in input_value:
        # プレフィックスが入力された場合はそのまま返す
        return input_value
    else:
        # サブネットマスクが入力された場合は変換して返す
        # サブネットマスクをドット区切りのリストに分割
        mask_parts = input_value.split('.')

        # サブネットマスクの各部分を2進数に変換し、連結してビット列を作成
        binary_mask = ''.join([bin(int(part))[2:].zfill(8) for part in mask_parts])

        # ビット列からプレフィックス長を計算
        prefix_length = str(len(binary_mask.rstrip('0')))

        return '/' + prefix_length

#prefixをサブネットマスクに変換する関数
def prefix_to_subnet_mask(prefix):
    try:
        network = ipaddress.IPv4Network(f'0.0.0.0/{prefix}', strict=False)
        return str(network.netmask)
    except ValueError:
        return "Invalid prefix"

# テキストを解析してデータを辞書に格納する関数
def parse_and_store_data(template_path, target_dict, config_data):
    with open(template_path) as template_file:
        fsm = textfsm.TextFSM(template_file)
        parsed_data = [dict(zip(fsm.header, item)) for item in fsm.ParseText(config_data)]
        for entry in parsed_data:
            name = entry["NAME"]
            if name not in target_dict:
                target_dict[name] = []
            target_dict[name].append(entry)

# ネットワークデータを処理する関数
def process_network_data(data):
    if data["HOST"]:
        type = "host"
        ip = data["HOST"]
    elif data["NETWORK"]:
        type = "network"
        ip = data["NETWORK"] + mask_or_prefix_to_prefix(data.get("NETMASK", "") + data.get("PREFIX_LENGTH", ""))
    elif data["START_IP"] and data["END_IP"]:
        type = "range"
        ip = data["START_IP"] + "-" + data["END_IP"]
    result = {"type": type,
              "ip": ip,
              }
    return result

def update_group_members(ntw):
    for name, values in ntw["grp"].items():
        updated_values = []
        for value in values:
            if value["TYPE"] == "group" and value["GRP_OBJECT"] in ntw["grp"]:
                values.extend(ntw["grp"][value["GRP_OBJECT"]])
            elif value["TYPE"] == "object" and value["NET_OBJECT"] in ntw["obj"]:
                updated_values.extend(ntw["obj"][value["NET_OBJECT"]])
            else:
                updated_values.append(value)
        ntw["grp"][name] = updated_values

# IPアドレスが範囲内にあるか確認する関数
def check_ip_in_range(target_ip, start_ip, end_ip):
    try:
        target_ip = ipaddress.IPv4Address(target_ip)
        start_ip = ipaddress.IPv4Address(start_ip)
        end_ip = ipaddress.IPv4Address(end_ip)

        return start_ip <= target_ip <= end_ip
    except ValueError:
        # IPアドレスが無効な場合に例外をキャッチします
        return False

# IPアドレスがネットワークに含まれるか確認する関数
def check_ip_in_network(target_ip, network):
    try:
        target_ip = ipaddress.IPv4Address(target_ip)
        network = ipaddress.IPv4Network(network, strict=False)  # strict=Falseでサブネットマスクが指定されていない場合もマッチするようにします

        return target_ip in network
    except ValueError:
        # IPアドレスまたはネットワークが無効な場合に例外をキャッチします
        return False

# IPアドレスが等しいか確認する関数
def check_ip_equal(target_ip, reference_ip):
    return target_ip == reference_ip

# reference_ipがtarget_netwrokのsubnetに含まれるか確認する関数
def check_network_in_network_subnet(target_network, reference_ip):
    network = ipaddress.IPv4Network(target_network, strict=False)
    reference_ip = ipaddress.IPv4Network(reference_ip)

    return reference_ip.subnet_of(network)

#IPアドレス範囲がすべてtartget_networkのsubnetに含まれるか確認する関数
def check_range_in_network_subnet(target_network, start_ip, end_ip):
    try:
        # IPレンジをサマリズしてサマリzedネットワークを取得
        summarized_networks = summarize_ip_range(start_ip, end_ip)

        # ターゲットネットワークがサマリzedネットワーク内に含まれるか確認
        target_network = ipaddress.IPv4Network(target_network, strict=False)
        for summarized_network in summarized_networks:
            if not(summarized_network.subnet_of(target_network)):
                return False
        return True

    except (ValueError, ipaddress.AddressValueError):
        # IPアドレスまたはネットワークが無効な場合に例外をキャッチします
        return False

def summarize_ip_range(start_ip, end_ip):
    try:
        start_ip = ipaddress.IPv4Address(start_ip)
        end_ip = ipaddress.IPv4Address(end_ip)

        # IPアドレスを要約して、サマリzedネットワークを取得
        summarized_networks = list(ipaddress.summarize_address_range(start_ip, end_ip))

        return summarized_networks
    except (ValueError, ipaddress.AddressValueError):
        # IPアドレスまたはネットワークが無効な場合に例外をキャッチします
        return []

def ip_match(target_ip, reference_ip, reference_type):
    if reference_type == "host":
        return check_ip_equal(target_ip, reference_ip)
    if reference_type == "network":
        return check_ip_in_network(target_ip, reference_ip)
    if reference_type == "range":
        start_ip, end_ip = reference_ip.split("-")
        return check_ip_in_range(target_ip, start_ip, end_ip)
    if reference_type == "any":
        return True

def ip_matchs(target_ip, reference_ips):
    flag = False
    for reference_ip in reference_ips:
        flag = flag or ip_match(target_ip, reference_ip["ip"], reference_ip["type"])
    return flag

def network_match(target_network, reference_ip, reference_type):
    if reference_type == "host" or reference_type == "network":
        return check_network_in_network_subnet(target_network, reference_ip)
    if reference_type == "range":
        start_ip, end_ip = reference_ip.split("-")
        return check_range_in_network_subnet(target_network, start_ip, end_ip)
    if reference_type == "any":
        return True

def network_matchs(target_network, reference_ips):
    flag = False
    for reference_ip in reference_ips:
        flag = flag or network_match(target_network, reference_ip["ip"], reference_ip["type"])
    return flag

def ips_matchs(target_ips, reference_ips):
    flag = True
    for target_ip in target_ips:
        if not ("/" in target_ip):
            flag = flag and ip_matchs(target_ip, reference_ips)
        else:
            flag = flag and network_matchs(target_ip, reference_ips)
    return flag

def is_ipv4_or_network_address(input_str):
    # IPアドレスの正規表現パターン
    ipv4_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    # ネットワークアドレス（CIDR表記）の正規表現パターン
    network_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$'

    # 正規表現パターンに一致するかどうかをチェック
    if re.match(ipv4_pattern, input_str) or re.match(network_pattern, input_str):
        return True
    else:
        return False

def is_ipv4_or_network_addresses(input_str):
    flag = True
    for address in input_str:
        flag = flag and is_ipv4_or_network_address(address)
    return flag

# オブジェクトネットワークデータを解析して格納
# Parse and store data for network objects and groups
def get_network():
    parse_and_store_data(ntw_obj_template, ntw["obj"], config_data)
    parse_and_store_data(ntw_grp_template, ntw["grp"], config_data)

    # 入れ子構造の解消
    update_group_members(ntw)

    ## ネットワークデータを処理しやすいように変形する関数
    for key, values in ntw["grp"].items():
        ntw["grp"][key] = [process_network_data(value) for value in values]

    for key, values in ntw["obj"].items():
        ntw["obj"][key] = [process_network_data(value) for value in values]

    return ntw

def main():
    ntw = get_network()
    target_ip = "192.168.255.1"
    for key, reference_ips in ntw["grp"].items():
            if (ip_matchs(target_ip, reference_ips)):
                print(key)
    for key, reference_ips in ntw["obj"].items():
            if (ip_matchs(target_ip, reference_ips)):
                print(key)

    print()
    target_network = "192.168.0.0/24"
    for key, reference_ips in ntw["grp"].items():
            if (network_matchs(target_network, reference_ips)):
                print(key)
    for key, reference_ips in ntw["obj"].items():
            if (network_matchs(target_network, reference_ips)):
                print(key)

if __name__ == "__main__":
    main()
