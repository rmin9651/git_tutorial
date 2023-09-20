import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import clipboard
import network_parse
import service_parse
import protocol_parse
import accesslist_parse
from pprint import pprint

def safe_get(seq, index, default=None):
    try:
        return seq[index]
    except IndexError:
        return default

def on_select_service(event):
    selected_items = tree_service.selection()
    selected_data = []
    for item in selected_items:
        values = tree_service.item(item, 'values')
        selected_data.append(values)

    if selected_data:
        # コピーしたデータを表示するか、他の処理を行うことができます
        print("Selected Data:", selected_data)
        # ここでクリップボードにデータをコピーする処理を追加することができます
        if (len(selected_data[0]) >= 2):
            clipboard.copy(selected_data[0][1])
    else:
        messagebox.showinfo("Information", "No item selected.")

def on_select_network(event):
    selected_items = tree_network.selection()
    selected_data = []
    for item in selected_items:
        values = tree_network.item(item, 'values')
        selected_data.append(values)

    if selected_data:
        # コピーしたデータを表示するか、他の処理を行うことができます
        print("Selected Data:", selected_data)
        # ここでクリップボードにデータをコピーする処理を追加することができます
        if (len(selected_data[0]) >= 2):
            clipboard.copy(selected_data[0][1])
    else:
        messagebox.showinfo("Information", "No item selected.")

def on_select_accesslist(event):
    selected_items = tree_accesslist.selection()
    selected_data = []
    for item in selected_items:
        values = tree_accesslist.item(item, 'values')
        selected_data.append(values)

    if selected_data:
        # コピーしたデータを表示するか、他の処理を行うことができます
        print("Selected Data:", selected_data)
        # ここでクリップボードにデータをコピーする処理を追加することができます
        if (len(selected_data[0]) >= 2):
            clipboard.copy(selected_data[0][1])
    else:
        messagebox.showinfo("Information", "No item selected.")

def load_file():
    global network_data, service_data, accesslist_data
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])  # テキストファイルを選択
    if file_path:
        # ファイルを読み込み、データを解析して取得する処理を実装
        with open(file_path, 'r') as file:
            config = file.read()
            network_data = network_parse.get_network(config)
            service_data = service_parse.get_service(config)
            accesslist_data = accesslist_parse.get_accesslist(config)
            init_network_tree()
            init_service_tree()
            init_accesslist_tree()

def service_clear_filter():
    for item in tree_service.get_children():
        tree_service.delete(item)  # すべてのセルを表示

def network_clear_filter():
    for item in tree_network.get_children():
        tree_network.delete(item)  # すべてのセルを表示

def accesslist_clear_filter():
    for item in tree_accesslist.get_children():
        tree_accesslist.delete(item)  # すべてのセルを表示

def init_network_tree():
    network_clear_filter()
    for category_name, category in network_data.items():
        parent_parent_item = tree_network.insert("", "end", values=category_name, open=True)
        for parent, values in category.items():
            parent_item = tree_network.insert(parent_parent_item, "end", values=("", parent), open=True)
            for value in values:
                ip = value["ip"]
                type = value["type"]
                tree_network.insert(parent_item, "end", values=("", "", ip, type))  # すべてのセルを表示

def filter_network_table():
    target_ip = filter_network_entry.get().lower().replace(" ", "").split(",")  # フィルターボックスからキーワードを取得し、小文字に変換
    if target_ip[0] == "":
        init_network_tree()
    if network_parse.is_ipv4_or_network_addresses(target_ip):
        temp_data = network_data.copy()
        network_clear_filter()
        for category_name, category in temp_data.items():
            parent_parent_item = tree_network.insert("", "end", values=category_name, open=True)
            for parent, values in category.items():
                if (network_parse.ips_matchs(target_ip, values)):
                    parent_item = tree_network.insert(parent_parent_item, "end", values=("", parent), open=True)
                    for value in values:
                        ip = value["ip"]
                        type = value["type"]
                        tree_network.insert(parent_item, "end", values=("", "", ip, type))  # すべてのセルを表示

def init_service_tree():
    service_clear_filter()
    for category_name, category in service_data.items():
        parent_parent_item = tree_service.insert("", "end", values=category_name, open=True)
        for parent, values in category.items():
            parent_item = tree_service.insert(parent_parent_item, "end", values=("", parent), open=True)
            for value in values:
                protocol = value["protocol"]
                src_ope = value["src_ope"]
                src_port = value["src_port"]
                dst_ope = value["dst_ope"]
                dst_port = value["dst_port"]
                tree_service.insert(parent_item, "end", values=("", "", protocol, src_ope, src_port, dst_ope, dst_port))  # すべてのセルを表示

def filter_service_table():
    target_port_protocol = filter_service_entry.get().lower().replace(" ", "").split(",")  # フィルターボックスからキーワードを取得し、小文字に変換
    if target_port_protocol[0] == "":
        init_service_tree()
    if service_parse.is_valid_ports_protocols(target_port_protocol):
        temp_data = service_data.copy()
        service_clear_filter()
        for category_name, category in temp_data.items():
            parent_parent_item = tree_service.insert("", "end", values=category_name, open=True)
            for parent, values in category.items():
                if (service_parse.srvs_multi_judge(target_port_protocol, values)):
                    parent_item = tree_service.insert(parent_parent_item, "end", values=("", parent), open=True)
                    for value in values:
                        protocol = value["protocol"]
                        src_ope = value["src_ope"]
                        src_port = value["src_port"]
                        dst_ope = value["dst_ope"]
                        dst_port = value["dst_port"]
                        tree_service.insert(parent_item, "end", values=("", "", protocol, src_ope, src_port, dst_ope, dst_port))  # すべてのセルを表示

def init_accesslist_tree():
    accesslist_clear_filter()
    for category_name, category in accesslist_data.items():
        parent_parent_item = tree_accesslist.insert("", "end", values=category_name, open=True)
        for values in category:
            parent_item = tree_accesslist.insert(parent_parent_item, "end", value=("", values["acl_all"], values["action"]), open=True)
            for i in range(max(len(values["srv"]), len(values["src"]), len(values["dst"]))):
                tree_accesslist.insert(parent_item, "end", values=("", "", "", safe_get(values["srv"], i, {}).get("protocol", ""), safe_get(values["src"], i, {}).get("ip", ""), safe_get(values["srv"], i, {}).get("src_ope", ""), safe_get(values["srv"], i, {}).get("src_port", ""), safe_get(values["dst"], i, {}).get("ip", ""), safe_get(values["srv"], i, {}).get("dst_ope", ""), safe_get(values["srv"], i, {}).get("dst_port", "")), open=True)

def filter_accesslist_table():
    target_src_ip = filter_SRC.get().lower().replace(" ", "").split(",")  # フィルターボックスからキーワードを取得し、小文字に変換
    target_dst_ip = filter_DST.get().lower().replace(" ", "").split(",")
    target_service = filter_SRV.get().lower().replace(" ", "").split(",")
    target_src_ip_flag = not target_src_ip[0] or network_parse.is_ipv4_or_network_addresses(target_src_ip)
    target_dst_ip_flag = not target_dst_ip[0] or network_parse.is_ipv4_or_network_addresses(target_dst_ip)
    target_service_flag = not target_service[0] or service_parse.is_valid_ports_protocols(target_service)
    if (not target_src_ip_flag or not target_dst_ip_flag or not target_service_flag):
        init()
    else:
        temp_data = accesslist_data.copy()
        accesslist_clear_filter()
        for category_name, category in temp_data.items():
            parent_parent_item = tree_accesslist.insert("", "end", values=category_name, open=True)
            for values in category:
                target_src_ip_flag = not target_src_ip[0] or network_parse.ips_matchs(target_src_ip, values["src"])
                target_dst_ip_flag = not target_dst_ip[0] or network_parse.ips_matchs(target_dst_ip, values["dst"])
                target_service_flag = not target_service[0] or service_parse.srvs_multi_judge(target_service, values["srv"])
                if (target_src_ip_flag and target_dst_ip_flag and target_service_flag):
                    parent_item = tree_accesslist.insert(parent_parent_item, "end", value=("", values["acl_all"], values["action"]), open=True)
                    for i in range(max(len(values["srv"]), len(values["src"]), len(values["dst"]))):
                        tree_accesslist.insert(parent_item, "end", values=("", "", "", safe_get(values["srv"], i, {}).get("protocol", ""), safe_get(values["src"], i, {}).get("ip", ""), safe_get(values["srv"], i, {}).get("src_ope", ""), safe_get(values["srv"], i, {}).get("src_port", ""), safe_get(values["dst"], i, {}).get("ip", ""), safe_get(values["srv"], i, {}).get("dst_ope", ""), safe_get(values["srv"], i, {}).get("dst_port", "")), open=True)


app = tk.Tk()
app.title("Cisco ASA")
app.geometry("1000x950")

# Create a notebook for tabs
notebook = ttk.Notebook(app)
notebook.pack(fill='both', expand=True)

# Create tabs
network_tab = ttk.Frame(notebook)
service_tab = ttk.Frame(notebook)
accesslist_tab = ttk.Frame(notebook)

# Add tabs to the notebook with titles
notebook.add(accesslist_tab, text="Access List Data")
notebook.add(network_tab, text="Network Data")
notebook.add(service_tab, text="Service Data")


# Create Treeview widgets for each tab
tree_accesslist = ttk.Treeview(accesslist_tab, columns=("Zone", "ACL", "Action", "Protocol", "SRC IP", "SRC ope", "SRC port", "DST IP", "DST ope", "DST port"), height=40)
tree_network = ttk.Treeview(network_tab, columns=("CATEGORY", "NAME", "IP", "TYPE"), height=40)
tree_service = ttk.Treeview(service_tab, columns=("CATEGORY", "NAME", "PROTOCOL", "SRC_OPE", "SRC_PORT", "DST_OPE", "DST_PORT"), height=40)

#access_list
tree_accesslist.heading("#1", text="Zone")
tree_accesslist.heading("#2", text="ACL")
tree_accesslist.heading("#3", text="Action")
tree_accesslist.heading("#4", text="Protocol")
tree_accesslist.heading("#5", text="SRC IP")
tree_accesslist.heading("#6", text="SRC ope")
tree_accesslist.heading("#7", text="SRC port")
tree_accesslist.heading("#8", text="DST IP")
tree_accesslist.heading("#9", text="DST ope")
tree_accesslist.heading("#10", text="DST port")

# Set column headings network
tree_network.heading("#1", text="CATEGORY")
tree_network.heading("#2", text="NAME")
tree_network.heading("#3", text="IP")
tree_network.heading("#4", text="TYPE")

#service
tree_service.heading("#1", text="CATEGORY")
tree_service.heading("#2", text="NAME")
tree_service.heading("#3", text="PROTOCOL")
tree_service.heading("#4", text="SRC_OPE")
tree_service.heading("#5", text="SRC_PORT")
tree_service.heading("#6", text="DST_OPE")
tree_service.heading("#7", text="DST_PORT")

# Set column widths access_list
tree_accesslist.column("#1", width=80)  # CATEGORY列の幅を100に設定
tree_accesslist.column("#3", width=80)  # NAME列の幅を150に設定
tree_accesslist.column("#4", width=80)  # NAME列の幅を150に設定
#tree_accesslist.column("#3", width=200)  # IP列の幅を100に設定
tree_accesslist.column("#6", width=80)  # TYPE列の幅を100に設定
tree_accesslist.column("#7", width=80)  # TYPE列の幅を100に設定
tree_accesslist.column("#9", width=80)  # TYPE列の幅を100に設定
tree_accesslist.column("#10", width=80)  # TYPE列の幅を100に設定

# Set column widths network
tree_network.column("#1", width=80)
tree_network.column("#2", width=150)
tree_network.column("#3", width=200)
tree_network.column("#4", width=100)

tree_service.column("#1", width=80)
tree_service.column("#2", width=150)
tree_service.column("#3", width=100)
tree_service.column("#4", width=100)
tree_service.column("#5", width=100)
tree_service.column("#6", width=100)
tree_service.column("#7", width=100)

# Sample data
accesslist_data = accesslist_parse.get_accesslist()
network_data = network_parse.get_network()
service_data = service_parse.get_service()

# Initialize the tree views with data
init_accesslist_tree()
init_network_tree()
init_service_tree()

# Bind events to the selection
tree_accesslist.bind("<<TreeviewSelect>>", on_select_accesslist)
tree_network.bind("<<TreeviewSelect>>", on_select_network)
tree_service.bind("<<TreeviewSelect>>", on_select_service)

#network tab
load_button = tk.Button(network_tab, text="Load File", command=load_file)
load_button.pack(anchor='nw', padx=10, pady=10)
filter_network_label = tk.Label(network_tab, text="Network Filter:")
filter_network_label.pack()
filter_network_entry = tk.Entry(network_tab, width=30)
filter_network_entry.pack()
filter_network_button = tk.Button(network_tab, text="Apply Filter", command=filter_network_table)
filter_network_button.pack()
clear_filter_network_button = tk.Button(network_tab, text="INIT", command=init_network_tree)
clear_filter_network_button.pack()
# Create vertical scrollbar for the network_tree
network_scrollbar_y = ttk.Scrollbar(network_tab, orient="vertical", command=tree_network.yview)
tree_network.configure(yscrollcommand=network_scrollbar_y.set)
network_scrollbar_y.pack(side="right", fill="y")
network_scrollbar_x = ttk.Scrollbar(network_tab, orient="horizontal", command=tree_network.xview)
tree_network.configure(xscrollcommand=network_scrollbar_x.set)
network_scrollbar_x.pack(side="bottom", fill="x")

#access_list
load_button = tk.Button(accesslist_tab, text="Load File", command=load_file)
load_button.pack(anchor='nw', padx=10, pady=10)

filter_accesslist_SRC = tk.Label(accesslist_tab, text="SRC_IP")
filter_accesslist_DST = tk.Label(accesslist_tab, text="DST_IP")
filter_accesslist_SRV = tk.Label(accesslist_tab, text="PORT")

filter_SRC = tk.Entry(accesslist_tab, width=80)
filter_DST = tk.Entry(accesslist_tab, width=80)
filter_SRV = tk.Entry(accesslist_tab, width=80)

filter_accesslist_SRC.pack(padx=5, pady=5, anchor="w")
filter_SRC.pack(padx=5, pady=5, fill="x")
filter_accesslist_DST.pack(padx=5, pady=5, anchor="w")
filter_DST.pack(padx=5, pady=5, fill="x")
filter_accesslist_SRV.pack(padx=5, pady=5, anchor="w")
filter_SRV.pack(padx=5, pady=5, fill="x")

filter_accesslist_button = tk.Button(accesslist_tab, text="Apply Filter", command=filter_accesslist_table)
clear_filter_accesslist_button = tk.Button(accesslist_tab, text="INIT", command=init_accesslist_tree)

filter_accesslist_button.pack(padx=5, pady=5)
clear_filter_accesslist_button.pack(padx=5, pady=5)

accesslist_scrollbar_y = ttk.Scrollbar(accesslist_tab, orient="vertical", command=tree_accesslist.yview)
tree_accesslist.configure(yscrollcommand=accesslist_scrollbar_y.set)
accesslist_scrollbar_y.pack(side="right", fill="y")
accesslist_scrollbar_x = ttk.Scrollbar(accesslist_tab, orient="horizontal", command=tree_accesslist.xview)
tree_accesslist.configure(xscrollcommand=accesslist_scrollbar_x.set)
accesslist_scrollbar_x.pack(side="bottom", fill="x")

#service tab
load_button = tk.Button(service_tab, text="Load File", command=load_file)
load_button.pack(anchor='nw', padx=10, pady=10)
filter_service_label = tk.Label(service_tab, text="Service Filter:")
filter_service_label.pack()
filter_service_entry = tk.Entry(service_tab, width=30)
filter_service_entry.pack()
filter_service_button = tk.Button(service_tab, text="Apply Filter", command=filter_service_table)
filter_service_button.pack()
clear_filter_service_button = tk.Button(service_tab, text="INIT", command=init_service_tree)
clear_filter_service_button.pack(after=filter_service_button)
# Create vertical scrollbar for the service_tree
service_scrollbar_y = ttk.Scrollbar(service_tab, orient="vertical", command=tree_service.yview)
tree_service.configure(yscrollcommand=service_scrollbar_y.set)
service_scrollbar_y.pack(side="right", fill="y")
service_scrollbar_x = ttk.Scrollbar(service_tab, orient="horizontal", command=tree_service.xview)
tree_service.configure(xscrollcommand=service_scrollbar_x.set)
service_scrollbar_x.pack(side="bottom", fill="x")

# Pack the Treeview widgets for each tab
tree_accesslist.pack(fill='both', expand=True)
tree_network.pack(fill='both', expand=True)
tree_service.pack(fill='both', expand=True)


app.mainloop()
