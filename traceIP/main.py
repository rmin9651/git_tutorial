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
def search_route(search_IP, device_name, route_type, route_info):
    if route_type == "asa":
        routes = route_info["asa"]
    elif route_type == "ios":
        routes = route_info["ios"]
    elif route_type == "nxos":
        routes = route_info["nxos"]
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
def search_next_device(nexthop_ip, route_info):
    for device_type, devices in route_info.items():
        for device_name, routes in devices.items():
            for route in routes:
                if (route["PROTOCOL"] in "L" or route["PROTOCOL"] in "local") and route["NETWORK"] == nexthop_ip:
                    return device_name, device_type
    return None, None

def get_valid_device_name(route_info):
    while True:
        device_name = input("Select a device name: ")
        for device_type, devices in route_info.items():
            if device_name in devices:
                return device_name, device_type
        print("Invalid device name. Please try again.")

def trace_route(search_IP, device, route_type, path, result, route_info, TTL=255, NEXTHOP_IP=""):
    #pdb.set_trace()
    #次のデバイスがないかTTLが0になったタイミングでresultを出力
    if (device is None and route_type is None) or TTL == 0:
        result_temp = path.copy()
        result_temp.append(NEXTHOP_IP)
        result.append(result_temp)  # パスのコピーをリストに追加
        return
    path.append(device)
    next_hops = search_route(search_IP, device, route_type, route_info)
    for next_hop in next_hops:
        next_device, next_route_type = search_next_device(next_hop["NEXTHOP_IP"], route_info)
        trace_route(search_IP, next_device, next_route_type, path, result, route_info, TTL-1, NEXTHOP_IP="")
    path.pop()  # 再帰呼び出し後にパスからデバイスを削除

def print_route(search_IP, routes, dst_IP):
    print(search_IP, end=" → ")
    for route in routes:
        if not route == "":
            print(route, end=" → ")
    print(dst_IP)

def main():
    route_info = {"asa":{}, "ios":{}, "nxos":{}}

    # ASAとiOSデバイスの設定ファイルのパスを取得
    asa_files = glob.glob("./config/asa/*.txt")
    ios_files = glob.glob("./config/ios/*.txt")
    nxos_files = glob.glob("./config/nxos/*.txt")

    #ASAとIOS、NXOSデバイスのテンプレートの設定
    asa_template = "./templates/cisco_asa_show_route.textfsm"
    ios_template = "./templates/cisco_ios_show_ip_route.textfsm"
    nxos_template = "./templates/cisco_nxos_show_ip_route.textfsm"

    # ASAデバイスのルート情報を抽出して辞書に格納
    for file in asa_files:
        route_info["asa"].update(extract_route_info(file, asa_template))

    # iOSデバイスのルート情報を抽出して辞書に格納
    for file in ios_files:
        route_info["ios"].update(extract_route_info(file, ios_template))

    # NXOSデバイスのルート情報を抽出して辞書に格納
    for file in nxos_files:
        route_info["nxos"].update(extract_route_info(file, nxos_template))


    # デバイス名の一覧表示
    search_IP = "192.168.254.3"
    dst_IP = "172.16.2.254"
    first_device, first_route_type = search_next_device(search_IP, route_info)

    if not first_device:
        print("Available device names:")
        for device_type, devices in route_info.items():
            for device_name in devices.keys():
                print("・" + device_name)
        # ユーザーからデバイス名の入力を受け取り、適切なデバイスタイプを設定
        before_device_name, before_route_type = get_valid_device_name(route_info)

        # 最初のデバイスからルート情報の検索を開始
        next = search_route(search_IP, before_device_name, before_route_type, route_info)
        next_device_name, next_route_type = search_next_device(next[0]["NEXTHOP_IP"], route_info)

        #無限ループを防ぐためTTLを255に設定
        for TTL in range(255):
            #もしNEXT_HOPのデバイスが見つからない場合、検索元をFirst Deviceとする。
            if next_device_name is None and next_route_type is None:
                first_device = before_device_name
                first_route_type = before_route_type
                break
            #ルート検索
            next = search_route(search_IP, next_device_name, next_route_type, route_info)
            #デバイスが検索元IPのセグメントを直接持っている場合First Deviceとする。
            if next[0]['PROTOCOL'] == "C" or next[0]['PROTOCOL'] == "direct":
                first_device = next_device_name
                first_route_type = next_route_type
                break
            #デバイスが検索元IPのセグメントを持っていない場合、次のデバイスを検索する。
            else:
                before_device_name = next_device_name
                before_route_type = next_route_type
                next_device_name, next_route_type = search_next_device(next[0]["NEXTHOP_IP"], route_info)

    result = []
    #ルートの検索
    next_hops = search_route(dst_IP, first_device, first_route_type, route_info)
    for next_hop in next_hops:
        next_device, next_route_type = search_next_device(next_hop["NEXTHOP_IP"], route_info)
        trace_route(dst_IP, next_device, next_route_type, [first_device], result, route_info)

    print("search_IP = " + str(search_IP) + "\t" + "Destination_IP = " + str(dst_IP))
    cnt = 1
    for route in result:
        print("\troute " + str(cnt), end="：")
        print_route(search_IP, route, dst_IP)
        cnt += 1

if __name__ == "__main__":
    main()
