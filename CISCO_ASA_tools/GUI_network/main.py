import tkinter as tk
from tkinter import ttk
from pprint import pprint
import tkinter.messagebox
import clipboard
import network_parse

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
        for parent, values in category.items():
            parent_item = tree.insert(parent_parent_item, "end", values=("", parent), open=True)
            for value in values:
                ip = value["ip"]
                type = value["type"]
                tree.insert(parent_item, "end", values=("", "", ip, type))  # すべてのセルを表示

def filter_table():
    target_ip = filter_entry.get().lower().replace(" ", "").split(",")  # フィルターボックスからキーワードを取得し、小文字に変換
    if target_ip[0] == "":
        init()
    if network_parse.is_ipv4_or_network_addresses(target_ip):
        temp_data = data.copy()
        clear_filter()
        for category_name, category in temp_data.items():
            parent_parent_item = tree.insert("", "end", values=category_name, open=True)
            for parent, values in category.items():
                if (network_parse.ips_matchs(target_ip, values)):
                    parent_item = tree.insert(parent_parent_item, "end", values=("", parent), open=True)
                    for value in values:
                        ip = value["ip"]
                        type = value["type"]
                        tree.insert(parent_item, "end", values=("", "", ip, type))  # すべてのセルを表示

app = tk.Tk()
app.title("Cisco ASA network")
app.geometry("800x950")
# Create Treeview widget
tree = ttk.Treeview(app, columns=("CATEGORY", "NAME", "IP", "TYPE"), height=40)
tree.heading("#1", text="CATEGORY")
tree.heading("#2", text="NAME")
tree.heading("#3", text="IP")
tree.heading("#4", text="TYPE")

# Set column widths
tree.column("#1", width=80)  # CATEGORY列の幅を100に設定
tree.column("#2", width=150)  # NAME列の幅を150に設定
tree.column("#3", width=200)  # IP列の幅を100に設定
tree.column("#4", width=100)  # TYPE列の幅を100に設定

# Sample data
data = network_parse.get_network()

# Insert data from the dictionary with a unique parent item
init()
# Bind an event to the selection
tree.bind("<<TreeviewSelect>>", on_select)

# Create a filter box
filter_label = tk.Label(app, text="Filter:")
filter_label.pack()
filter_entry = tk.Entry(app, width = 80)
filter_entry.pack()
filter_button = tk.Button(app, text="Apply Filter", command=filter_table)
filter_button.pack()
clear_filter_button = tk.Button(app, text="INIT", command=init)
clear_filter_button.pack()

tree.pack()
app.mainloop()
