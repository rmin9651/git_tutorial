import tkinter as tk
from tkinter import ttk
from pprint import pprint
import tkinter.messagebox
import clipboard
import service_parse

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
                protocol = value["protocol"]
                src_ope = value["src_ope"]
                src_port = value["src_port"]
                dst_ope = value["dst_ope"]
                dst_port= value["dst_port"]
                tree.insert(parent_item, "end", values=("", "", protocol, src_ope, src_port, dst_ope, dst_port))  # すべてのセルを表示


def filter_table():
    target_port_protocol = filter_entry.get().lower().replace(" ", "").split(",")  # フィルターボックスからキーワードを取得し、小文字に変換
    if target_port_protocol[0] == "":
        init()
    if service_parse.is_valid_ports_protocols(target_port_protocol):
        temp_data = data.copy()
        clear_filter()
        for category_name, category in temp_data.items():
            parent_parent_item = tree.insert("", "end", values=category_name, open=True)
            for parent, values in category.items():
                if (service_parse.srvs_multi_judge(target_port_protocol, values)):
                    parent_item = tree.insert(parent_parent_item, "end", values=("", parent), open=True)
                    for value in values:
                        protocol = value["protocol"]
                        src_ope = value["src_ope"]
                        src_port = value["src_port"]
                        dst_ope = value["dst_ope"]
                        dst_port= value["dst_port"]
                        tree.insert(parent_item, "end", values=("", "", protocol, src_ope, src_port, dst_ope, dst_port))  # すべてのセルを表示

app = tk.Tk()
app.title("Cisco ASA service")
app.geometry("1000x950")
# Create Treeview widget
tree = ttk.Treeview(app, columns=("CATEGORY", "NAME", "PROTOCOL", "SRC_OPE", "SRC_PORT", "DST_OPE", "DST_PORT"), height=40)
tree.heading("#1", text="CATEGORY")
tree.heading("#2", text="NAME")
tree.heading("#3", text="PROTOCOL")
tree.heading("#4", text="SRC_OPE")
tree.heading("#5", text="SRC_PORT")
tree.heading("#6", text="DST_OPE")
tree.heading("#7", text="DST_PORT")

# Set column widths
tree.column("#1", width=80)
tree.column("#2", width=150)
tree.column("#3", width=100)
tree.column("#4", width=100)
tree.column("#5", width=100)
tree.column("#6", width=100)
tree.column("#7", width=100)

# Sample data
data = service_parse.get_service()

# Insert data from the dictionary with a unique parent item
init()
# Bind an event to the selection
tree.bind("<<TreeviewSelect>>", on_select)

# Create a filter box
filter_label = tk.Label(app, text="Filter:")
filter_label.pack()
filter_entry = tk.Entry(app, width = 30)
filter_entry.pack()
filter_button = tk.Button(app, text="Apply Filter", command=filter_table)
filter_button.pack()
clear_filter_button = tk.Button(app, text="INIT", command=init)
clear_filter_button.pack()

tree.pack()
app.mainloop()
