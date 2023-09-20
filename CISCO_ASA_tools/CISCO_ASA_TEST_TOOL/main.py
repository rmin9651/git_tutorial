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
import openpyxl

def safe_get(seq, index, default=None):
    try:
        return seq[index]
    except IndexError:
        return default

# Sample data
accesslist_datas = accesslist_parse.get_accesslist()

target_name = "inside"
target_src_ip = "10.21.10.5"
target_dst_ip = "10.50.20.10"
target_protocol = "tcp"
target_port = "80"


for name,  accesslists in accesslist_datas.items():
    for accesslist in accesslists:
        target_name_flag = (target_name == name)
        target_src_ip_flag = network_parse.ip_matchs(target_src_ip, accesslist["src"])
        target_dst_ip_flag = network_parse.ip_matchs(target_dst_ip, accesslist["dst"])
        target_service_flag = service_parse.srvs_judge(target_protocol, target_port, accesslist["srv"])
        if (target_name_flag and target_src_ip_flag and target_dst_ip_flag and target_service_flag):
            if (accesslist["action"] == "permit"):
                print(accesslist['acl_all'])
                print("srcIP")
                pprint(accesslist['src'])
                print("dstIP")
                pprint(accesslist['dst'])
                print("service")
                pprint(accesslist['srv'])
                break
            else:
                print(accesslist['acl_all'])
