import os
import glob
import textfsm
from pprint import pprint
import ipaddress

def prefix_to_subnet_mask(prefix):
    try:
        network = ipaddress.IPv4Network(f'0.0.0.0/{prefix}', strict=False)
        return str(network.netmask)
    except ValueError:
        return "Invalid prefix"

# デバイス名を抽出し、ルート情報を辞書に格納する関数
def extract_route_info(file_path, template_path):
    device_name = os.path.basename(file_path).split('.')[0]  # ファイルパスからデバイス名を抽出
    try:
        with open(file_path) as f:
            conf = f.read()  # 設定ファイルを読み込む

        with open(template_path) as ftemplate:
            fsm = textfsm.TextFSM(ftemplate)  # テキストFSMテンプレートを使用してルート情報を抽出
            return {device_name: [dict(zip(fsm.header, item)) for item in fsm.ParseText(conf)]}
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return {}  # エラーが発生した場合、空の辞書を返す

def serch_route(search_IP, device_name, type):
    if type == "ios":
        routes = ios_route[device_name]
    elif type == "asa":
        routes = asa_route[device_name]
    match_route = list()
    search_IP = ipaddress.IPv4Address(search_IP)
    for route in routes:
        network = ipaddress.IPv4Network(route["NETWORK"]+"/"+route.get("NETMASK", "") + route.get("PREFIX_LENGTH", ""), strict=False)
        if search_IP in network:
            match_route.append(route)
    result = list()
    for prefix in range(32,-1, -1):
        for route in match_route:
            if prefix_to_subnet_mask(route.get("NETMASK", "") + route.get("PREFIX_LENGTH", "")) == prefix_to_subnet_mask(prefix):
                result.append(route)
        if result:
            return result

def search_next_device(nexthop_ip):
    for device_name, routes in asa_route.items():
        for route in routes:
            if route["PROTOCOL"] in "L":
                if route["NETWORK"] == nexthop_ip:
                    next_device_name = device_name
                    type = "asa"

    for device_name, routes in ios_route.items():
        for route in routes:
            if route["PROTOCOL"] in "L":
                if route["NETWORK"] == nexthop_ip:
                    next_device_name = device_name
                    type = "ios"
    return next_device_name, type

asa_route = dict()  # ASAデバイスのルート情報を格納する辞書
ios_route = dict()  # iOSデバイスのルート情報を格納する辞書

# ASAとiOSデバイスの設定ファイルのパスを取得
asa_files = glob.glob("./config/asa/*.txt")
ios_files = glob.glob("./config/ios/*.txt")

asa_template = "./templates/cisco_asa_show_route.textfsm"  # ASAのテンプレートファイル
ios_template = "./templates/cisco_ios_show_ip_route.textfsm"  # iOSのテンプレートファイル

# ASAデバイスのルート情報を抽出して辞書に格納
for file in asa_files:
    asa_route.update(extract_route_info(file, asa_template))

# iOSデバイスのルート情報を抽出して辞書に格納
for file in ios_files:
    ios_route.update(extract_route_info(file, ios_template))

search_IP = ipaddress.IPv4Address("172.16.1.1")

next = serch_route(search_IP, "A-ASA-01", "asa")
next_device_name, type = search_next_device(next[0]["NEXTHOP_IP"])
print(next_device_name, type)
while(True):
    next = serch_route(search_IP, next_device_name, type)
    if next[0]['PROTOCOL'] == "C":
        break
    else:
        next_device_name, type = search_next_device(next[0]["NEXTHOP_IP"])
        print(next_device_name, type)
