import networkx as nx #networkxのインポート
from matplotlib import pyplot as plt #matplotlibのインポート
import glob
import os
import textfsm
from pprint import pprint
import ipaddress
from pyvis.network import Network
import tkinter as tk
from tkinter import ttk
from tkinter import Canvas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

def prefix_to_subnet_mask(prefix):
    try:
        network = ipaddress.IPv4Network(f'0.0.0.0/{prefix}', strict=False)
        return str(network.netmask)
    except ValueError:
        return "Invalid prefix"

def extract_route_info(file_path, template_path):
    device_name = os.path.basename(file_path).split('.')[0]
    print(device_name)
    try:
        with open(file_path) as f:
            conf = f.read()
        with open(template_path) as ftemplate:
            fsm = textfsm.TextFSM(ftemplate)
            return {device_name: [dict(zip(fsm.header, item)) for item in fsm.ParseText(conf)]}
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return {}

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

def check_device(text, route_info):
    for device_type, devices in route_info.items():
        if text in devices:
            return True
    return False

def get_device_route(device_types, templates):
    # デバイスのルート情報を抽出して辞書に格納
    route_info = {"asa": {}, "ios": {}, "nxos": {}}
    for device_type, file_pattern in device_types.items():
        files = glob.glob(file_pattern)
        template_path = templates[device_type]
        for file in files:
            route_info[device_type].update(extract_route_info(file, template_path))
    return route_info

def serch_first_device(sourceIP, route_info):
    # ユーザーからデバイス名の入力を受け取り、適切なデバイスタイプを設定
    before_device_name = v.get()
    before_route_type = Search_Device_Type(before_device_name, route_info)
    # 最初のデバイスからルート情報の検索を開始
    next = search_route(sourceIP, before_device_name, before_route_type, route_info)
    next_device_name, next_route_type = search_next_device(next[0]["NEXTHOP_IP"], route_info)

    #無限ループを防ぐためTTLを255に設定
    for TTL in range(255):
        #もしNEXT_HOPのデバイスが見つからない場合、検索元をFirst Deviceとする。
        if next_device_name is None and next_route_type is None:
            first_device = before_device_name
            first_route_type = before_route_type
            break
        #ルート検索
        next = search_route(sourceIP, next_device_name, next_route_type, route_info)
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
    return first_device, first_route_type

def Search_Device_Type(device_name, route_info):
    for device_type, devices in route_info.items():
        if device_name in devices:
            return device_type
    return None

def Search():
    sourceIP = SourceIP_Entry.get()
    destinationIP = DestinationIP_Entry.get()
    Caution_Label["text"] = ""
    first_device, first_route_type = search_next_device(sourceIP, route_info)
    if not first_device:
        if v.get() == "":
            Caution_Label["text"] = "FirstDeviceを指定してください"
            return
        first_device, first_route_type = serch_first_device(sourceIP, route_info)
    result = []
    #ルートの検索
    next_hops = search_route(destinationIP, first_device, first_route_type, route_info)
    for next_hop in next_hops:
        next_device, next_route_type = search_next_device(next_hop["NEXTHOP_IP"], route_info)
        trace_route(destinationIP, next_device, next_route_type, [first_device], result, route_info)

    print("SourceIP = " + str(sourceIP) + "\t" + "Destination_IP = " + str(destinationIP))
    cnt = 1
    for route in result:
        print("\troute " + str(cnt), end="：")
        print_route(sourceIP, route, destinationIP)
        cnt += 1

G = nx.Graph()
device_types = {"asa": "./config/asa/*.txt", "ios": "./config/ios/*.txt", "nxos": "./config/nxos/*.txt"}
templates = {"asa": "./templates/cisco_asa_show_route.textfsm",
             "ios": "./templates/cisco_ios_show_ip_route.textfsm",
             "nxos": "./templates/cisco_nxos_show_ip_route.textfsm"}
devices_name = list()

# デバイスのルート情報を抽出して辞書に格納
route_info = get_device_route(device_types, templates)

for device_type, devices in route_info.items():
    for device_name in devices.keys():
        devices_name.append(device_name)

for device_type, devices in route_info.items():
    for device_name in devices.keys():
        G.add_node(device_name)

connecteds = list()
result = list()
for device_type, devices in route_info.items():
    for device_name, device_routes in devices.items():
        for route in device_routes:
            if route["PROTOCOL"] == "C":
                connected_route = ipaddress.IPv4Network(route["NETWORK"] + "/" + (route.get("NETMASK", "") + route.get("PREFIX_LENGTH", "")), strict=False)
                G.add_node(str(connected_route))
                connecteds.append(connected_route)

for connected in connecteds:
    for device_type, devices in route_info.items():
        for device_name, device_routes in devices.items():
            for route in device_routes:
                if route["PROTOCOL"] == "C":
                    connected_route = ipaddress.IPv4Network(route["NETWORK"] + "/" + (route.get("NETMASK", "") + route.get("PREFIX_LENGTH", "")), strict=False)
                    if connected == connected_route:
                        result.append((str(connected), device_name))

G.add_edges_from(result) #エッジもまとめて追加することができる

    # tkinter ウィンドウの作成
root = tk.Tk()
root.title("Trace IP")
root.geometry("1200x700")

frame01 = ttk.Frame(root)
frame01.pack(fill=tk.X, pady=10)
frame02 = ttk.Frame(root)
frame02.pack(fill=tk.X, pady=1)
frame03 = ttk.Frame(root)
frame03.pack(fill=tk.X, pady=1)
frame04 = ttk.Frame(root)
frame04.pack(fill=tk.X, pady=1)
frame05 = ttk.Frame(root)
frame05.pack(fill=tk.X, pady=1)
# matplotlib の Figure を作成
fig = Figure(figsize=(15, 3))
fig.subplots_adjust(left=0.05, right=0.95, bottom=0.01, top=1)
ax = fig.add_subplot(111)


# networkx のグラフを matplotlib の Figure に描画
pos = nx.spring_layout(G, seed=3)
node_size = [100 if check_device(n, route_info) else 1 for (n,d) in G.nodes(data=True)]
nx.draw_networkx_nodes(G, pos, alpha=0.6, node_size=node_size, ax=ax)
nx.draw_networkx_labels(G, pos, font_size=10, font_family="Yu Gothic", font_weight="bold", ax=ax)
nx.draw_networkx_edges(G, pos, alpha=0.4, edge_color=[0] * len(G.edges), ax=ax)

# Figure を tkinter の Canvas に埋め込む
canvas = FigureCanvasTkAgg(fig, master=frame01)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# ツールバーを追加
toolbar = NavigationToolbar2Tk(canvas, frame01)
canvas_widget.config(scrollregion=canvas_widget.bbox("all"))
toolbar.update()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Sourceウィジェットを作成
SourceIP_Label = tk.Label(frame02, text="SourceIP：        ")
SourceIP_Label.pack(side=tk.LEFT)
SourceIP_Entry = tk.Entry(frame02, width=80)
SourceIP_Entry.pack(side=tk.LEFT, pady=1)

# Destinationウィジェットを作成
DestinationIP_Label = tk.Label(frame03, text="DestinationIP：")
DestinationIP_Label.pack(side=tk.LEFT)
DestinationIP_Entry = tk.Entry(frame03, width=80)
DestinationIP_Entry.pack(side=tk.LEFT, pady=1)

# First Deviceウィジェットを作成
v = tk.StringVar()
FirstDevice_Label = tk.Label(frame04, text="FirstDeviceIP：")
FirstDevice_Label.pack(side=tk.LEFT)
FirstDevice_comb = ttk.Combobox(
    frame04, textvariable=v,
    values=devices_name, width=10)
FirstDevice_comb.pack(side=tk.LEFT)
Caution_Label = tk.Label(frame04)
Caution_Label.pack(side=tk.LEFT)

# Buttonウィジェットを作成
Search_Label = tk.Label(frame05, text="Search: ")
Search_Label.pack(side=tk.LEFT)
Search_Button = tk.Button(frame05, text="Search", command=Search)
Search_Button.pack(side=tk.LEFT)
# tkinter ウィンドウを表示
root.mainloop()

#    net = Network()
#    nx.draw(G, node_color="red", with_labels=True)
#    net.from_nx(G)
#    net.show("pyvis.html", notebook=False)
