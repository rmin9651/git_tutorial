import tkinter as tk
from tkinter import ttk
from pprint import pprint
import tkinter.messagebox
import clipboard
import network_parse
import service_parse
import protocol_parse
import access_list_parse

def safe_get(seq, index, default=None):
    try:
        return seq[index]
    except IndexError:
        return default

def on_select(event):
    selected_items = tree.selection()
    selected_data = []
    for item in selected_items:
        values = tree.item(item, 'values')
        selected_data.append(values)

    if selected_data:
        # コピーしたデータを表示するか、他の処理を行うことができます
        print("Selected Data:", selected_data)
        # ここでクリップボードにデータをコピーする処理を追加することができます
        if (len(selected_data[0]) >= 2):
            clipboard.copy(selected_data[0][1])
    else:
        tkinter.messagebox.showinfo("Information", "No item selected.")
def clear_filter():
    for item in tree.get_children():
        tree.delete(item)  # すべてのセルを表示

def init():
    clear_filter()
    for category_name, category in data.items():
        parent_parent_item = tree.insert("", "end", values=category_name, open=True)
        for values in category:
            parent_item = tree.insert(parent_parent_item, "end", value=("", values["acl_all"], values["action"]), open=True)
            for i in range(max(len(values["srv"]), len(values["src"]), len(values["dst"]))):
                tree.insert(parent_item, "end", values=("", "", "", safe_get(values["srv"], i, {}).get("protocol", ""), safe_get(values["src"], i, {}).get("ip", ""), safe_get(values["srv"], i, {}).get("src_ope", ""), safe_get(values["srv"], i, {}).get("src_port", ""), safe_get(values["dst"], i, {}).get("ip", ""), safe_get(values["srv"], i, {}).get("dst_ope", ""), safe_get(values["srv"], i, {}).get("dst_port", "")), open=True)

def filter_table():
    target_src_ip = filter_SRC.get().lower().replace(" ", "").split(",")  # フィルターボックスからキーワードを取得し、小文字に変換
    target_dst_ip = filter_DST.get().lower().replace(" ", "").split(",")
    target_service = filter_SRV.get().lower().replace(" ", "").split(",")
    target_src_ip_flag = not target_src_ip[0] or network_parse.is_ipv4_or_network_addresses(target_src_ip)
    target_dst_ip_flag = not target_dst_ip[0] or network_parse.is_ipv4_or_network_addresses(target_dst_ip)
    target_service_flag = not target_service[0] or service_parse.is_valid_ports_protocols(target_service)
    if (not target_src_ip_flag or not target_dst_ip_flag or not target_service_flag):
        init()
    else:
        temp_data = data.copy()
        clear_filter()
        for category_name, category in data.items():
            parent_parent_item = tree.insert("", "end", values=category_name, open=True)
            for values in category:
                target_src_ip_flag = not target_src_ip[0] or network_parse.ips_matchs(target_src_ip, values["src"])
                target_dst_ip_flag = not target_dst_ip[0] or network_parse.ips_matchs(target_dst_ip, values["dst"])
                target_service_flag = not target_service[0] or service_parse.srvs_multi_judge(target_service, values["srv"])
                if (target_src_ip_flag and target_dst_ip_flag and target_service_flag):
                    parent_item = tree.insert(parent_parent_item, "end", value=("", values["acl_all"], values["action"]), open=True)
                    for i in range(max(len(values["srv"]), len(values["src"]), len(values["dst"]))):
                        tree.insert(parent_item, "end", values=("", "", "", safe_get(values["srv"], i, {}).get("protocol", ""), safe_get(values["src"], i, {}).get("ip", ""), safe_get(values["srv"], i, {}).get("src_ope", ""), safe_get(values["srv"], i, {}).get("src_port", ""), safe_get(values["dst"], i, {}).get("ip", ""), safe_get(values["srv"], i, {}).get("dst_ope", ""), safe_get(values["srv"], i, {}).get("dst_port", "")), open=True)

app = tk.Tk()
app.title("Cisco ASA network")
app.geometry("1500x1200")
# Create Treeview widget
tree = ttk.Treeview(app, columns=("Zone", "ACL", "Action", "Protocol", "SRC IP", "SRC ope", "SRC port", "DST IP", "DST ope", "DST port"), height=40)
tree.heading("#1", text="Zone")
tree.heading("#2", text="ACL")
tree.heading("#3", text="Action")
tree.heading("#4", text="Protocol")
tree.heading("#5", text="SRC IP")
tree.heading("#6", text="SRC ope")
tree.heading("#7", text="SRC port")
tree.heading("#8", text="DST IP")
tree.heading("#9", text="DST ope")
tree.heading("#10", text="DST port")

# Set column widths
tree.column("#1", width=80)  # CATEGORY列の幅を100に設定
tree.column("#3", width=80)  # NAME列の幅を150に設定
tree.column("#4", width=80)  # NAME列の幅を150に設定
#tree.column("#3", width=200)  # IP列の幅を100に設定
tree.column("#6", width=80)  # TYPE列の幅を100に設定
tree.column("#7", width=80)  # TYPE列の幅を100に設定
tree.column("#9", width=80)  # TYPE列の幅を100に設定
tree.column("#10", width=80)  # TYPE列の幅を100に設定


# Sample data
data = access_list_parse.get_access_list()
pprint(data)

# Insert data from the dictionary with a unique parent item
init()
# Bind an event to the selection
tree.bind("<<TreeviewSelect>>", on_select)

# Create a filter box
label_1 = tk.Label(app, text="SRC_IP")
label_2 = tk.Label(app, text="DST_IP")
label_3 = tk.Label(app, text="PORT")

filter_SRC = tk.Entry(app, width=80)
filter_DST = tk.Entry(app, width=80)
filter_SRV = tk.Entry(app, width=80)

label_1.grid(row=0, column=0, padx=5, pady=5)
filter_SRC.grid(row=0, column=1, padx=5, pady=5)
label_2.grid(row=1, column=0, padx=5, pady=5)
filter_DST.grid(row=1, column=1, padx=5, pady=5)
label_3.grid(row=2, column=0, padx=5, pady=5)
filter_SRV.grid(row=2, column=1, padx=5, pady=5)

filter_button = tk.Button(app, text="Apply Filter", command=filter_table)
clear_filter_button = tk.Button(app, text="INIT", command=init)

filter_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
clear_filter_button.grid(row=3, column=2, columnspan=2, padx=5, pady=5)
tree.grid(row=4, column=1, columnspan=4)

app.mainloop()
