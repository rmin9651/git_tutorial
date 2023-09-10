import os
import glob
import textfsm
import ipaddress
import pdb
from pprint import pprint

# プレフィックスをサブネットマスクに変換する関数
def prefix_to_subnet_mask(prefix):
    try:
        network = ipaddress.IPv4Network(f'0.0.0.0/{prefix}', strict=False)
        return str(network.netmask)
    except ValueError:
        return "Invalid prefix"

# デバイス名を抽出し、ルート情報を辞書に格納する関数
def extract_route_info(file_path, template_path):
    device_name = os.path.basename(file_path).split('.')[0]
    try:
        with open(file_path) as f:
            conf = f.read()
        with open(template_path) as ftemplate:
            fsm = textfsm.TextFSM(ftemplate)
            return {device_name: [dict(zip(fsm.header, item)) for item in fsm.ParseText(conf)]}
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return {}

# ルート情報を検索する関数
def search_route(search_IP, device_name, route_type):
    routes = asa_route if route_type == "asa" else ios_route
    match_route = []
    search_IP = ipaddress.IPv4Address(search_IP)
    for route in routes[device_name]:
        network = ipaddress.IPv4Network(route["NETWORK"] + "/" + (route.get("NETMASK", "") + route.get("PREFIX_LENGTH", "")), strict=False)
        if search_IP in network:
            match_route.append(route)
    result = []
    for prefix in range(32, -1, -1):
        for route in match_route:
            if prefix_to_subnet_mask(route.get("NETMASK", "") + route.get("PREFIX_LENGTH", "")) == prefix_to_subnet_mask(prefix):
                result.append(route)
        if result:
            return result

# 次のデバイスを検索する関数
def search_next_device(nexthop_ip):
    for device_name, routes in asa_route.items():
        for route in routes:
            if route["PROTOCOL"] in "L" and route["NETWORK"] == nexthop_ip:
                return device_name, "asa"
    for device_name, routes in ios_route.items():
        for route in routes:
            if route["PROTOCOL"] in "L" and route["NETWORK"] == nexthop_ip:
                return device_name, "ios"
    return None, None

def get_valid_device_name():
    while True:
        device_name = input("Select a device name: ")
        if device_name in asa_route:
            return device_name, "asa"
        elif device_name in ios_route:
            return device_name, "ios"
        else:
            print("Invalid device name. Please try again.")

def trace_route(search_IP, device, route_type, path):
    #pdb.set_trace()
    path.append(device)
    next_hops = search_route(search_IP, device, route_type)
    for next_hop in next_hops:
        next_device, route_type = search_next_device(next_hop["NEXTHOP_IP"])
        if next_hop['PROTOCOL'] == "C" or (next_device is None and route_type is None):
            return print(path)
        trace_route(search_IP, next_device, route_type, path.copy())

def trace_route_ver2(search_IP, device, route_type, path, result):
    #pdb.set_trace()
    if device is None and route_type is None:
        result.append(path.copy())  # パスのコピーをリストに追加
        return
    path.append(device)
    next_hops = search_route(search_IP, device, route_type)
    for next_hop in next_hops:
        next_device, next_route_type = search_next_device(next_hop["NEXTHOP_IP"])
        trace_route_ver2(search_IP, next_device, next_route_type, path, result)
    path.pop()  # 再帰呼び出し後にパスからデバイスを削除



asa_route, ios_route = {}, {}

# ASAとiOSデバイスの設定ファイルのパスを取得
asa_files = glob.glob("./config/asa/*.txt")
ios_files = glob.glob("./config/ios/*.txt")

asa_template = "./templates/cisco_asa_show_route.textfsm"
ios_template = "./templates/cisco_ios_show_ip_route.textfsm"

# ASAデバイスのルート情報を抽出して辞書に格納
for file in asa_files:
    asa_route.update(extract_route_info(file, asa_template))

# iOSデバイスのルート情報を抽出して辞書に格納
for file in ios_files:
    ios_route.update(extract_route_info(file, ios_template))

# デバイス名の一覧表示
search_IP = "192.168.254.254"
dst_IP = "172.16.2.254"
first_device, first_route_type = search_next_device(search_IP)

if not first_device:
    print("Available device names:")
    for device_name in asa_route.keys():
        print("・" + device_name)
    for device_name in ios_route.keys():
        print("・" + device_name)
    # ユーザーからデバイス名の入力を受け取り、適切なデバイスタイプを設定
    device_name, type = get_valid_device_name()
    # 最初のデバイスからルート情報の検索を開始
    next = search_route(search_IP, device_name, type)
    next_device_name, route_type = search_next_device(next[0]["NEXTHOP_IP"])
    while True:
        next = search_route(search_IP, next_device_name, route_type)
        if next[0]['PROTOCOL'] == "C":
            first_device = next_device_name
            first_route_type = route_type
            break
        else:
            next_device_name, route_type = search_next_device(next[0]["NEXTHOP_IP"])

trace_route(dst_IP, first_device, first_route_type, [])

result = []
next_hops = search_route(dst_IP, first_device, first_route_type)
for next_hop in next_hops:
    next_device, next_route_type = search_next_device(next_hop["NEXTHOP_IP"])
    trace_route_ver2(dst_IP, next_device, next_route_type, [first_device], result)
pprint(result)
