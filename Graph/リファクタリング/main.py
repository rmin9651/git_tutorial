from ASA import ASA
from IOS import IOS
from NXOS import NXOS
from VIRTUAL import VIRTUAL
from NWGraph import NWGraph
import textfsm
import glob
import os
import copy
import networkx as nx #networkxのインポート
from matplotlib import pyplot as plt #matplotlibのインポート
from tkinter import ttk
import tkinter as tk
from tkinter import Canvas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class Application(ttk.Frame):
    def __init__(self,master, Devices):
        super().__init__(master)
        self.pack()
        master.geometry("1200x700")
        master.title("TraceIP")

        NWG = NWGraph(Devices)
        self.create_NWGwidgets(NWG)

        self.Devices = Devices
        self.create_TraceIPwidgets()

    def create_NWGwidgets(self, NWG):
        self.NWGFrame = tk.Frame(self)
        self.NWGFrame.pack(fill=tk.X, pady=10)

        self.fig = Figure(figsize=(15, 3))
        self.fig.subplots_adjust(left=0.05, right=0.95, bottom=0.01, top=1)
        self.ax = self.fig.add_subplot(111)

        self.pos = nx.spring_layout(NWG.G, seed=3)
        nx.draw_networkx_nodes(NWG.G, self.pos, alpha=0.6, node_size=NWG.node_size, ax=self.ax)
        nx.draw_networkx_labels(NWG.G, self.pos, font_size=10, font_family="Yu Gothic", font_weight="bold", ax=self.ax)
        nx.draw_networkx_edges(NWG.G, self.pos, alpha=0.4, edge_color=[0] * len(NWG.G.edges), ax=self.ax)

        # Figure を tkinter の Canvas に埋め込む
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.NWGFrame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # ツールバーを追加
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.NWGFrame)
        self.canvas_widget.config(scrollregion=self.canvas_widget.bbox("all"))
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def create_TraceIPwidgets(self):
        self.SourceIPFrame = tk.Frame(self)
        self.SourceIPFrame.pack(fill=tk.X, pady=1)
        self.SourceIP_Label = tk.Label(self.SourceIPFrame, text="SourceIP：        ")
        self.SourceIP_Label.pack(side=tk.LEFT)
        self.SourceIP_Entry = tk.Entry(self.SourceIPFrame, width=80)
        self.SourceIP_Entry.pack(side=tk.LEFT, pady=1)

        self.DestinationIPFrame = tk.Frame(self)
        self.DestinationIPFrame.pack(fill=tk.X, pady=1)
        self.DestinationIP_Label = tk.Label(self.DestinationIPFrame, text="DestinationIP：")
        self.DestinationIP_Label.pack(side=tk.LEFT)
        self.DestinationIP_Entry = tk.Entry(self.DestinationIPFrame, width=80)
        self.DestinationIP_Entry.pack(side=tk.LEFT, pady=1)

        self.selectDevice = tk.StringVar()
        self.selectSearchDeviceFrame = ttk.Frame(self)
        self.selectSearchDeviceFrame.pack(fill=tk.X, pady=1)
        self.SelectDevice_Label = tk.Label(self.selectSearchDeviceFrame, text="Select Search Device：")
        self.SelectDevice_Label.pack(side=tk.LEFT)
        self.SelectDevice_comb = ttk.Combobox(
            self.selectSearchDeviceFrame, textvariable=self.selectDevice,
            values=[Device.get_name() for Device in self.Devices], width=10)
        self.SelectDevice_comb.pack(side=tk.LEFT)
        self.Caution_Label = tk.Label(self.selectSearchDeviceFrame)
        self.Caution_Label.pack(side=tk.LEFT)

        self.SearchButtonFrame = ttk.Frame(self)
        self.SearchButtonFrame.pack(fill=tk.X, pady=1)
        self.Search_Label = tk.Label(self.SearchButtonFrame, text="Search: ")
        self.Search_Label.pack(side=tk.LEFT)
        self.Search_Button = tk.Button(self.SearchButtonFrame, text="Search", command=self.searchRoute)
        self.Search_Button.pack(side=tk.LEFT)

        self.SearchResultFrame = ttk.Frame(self)
        self.SearchResultFrame.pack(fill=tk.X, pady=1)
        self.SearchResult_Label = tk.Label(self.SearchResultFrame, text="Path: ")
        self.SearchResult_Label.pack()
        self.Result_Label = tk.Label(self.SearchResultFrame, text="")
        self.Result_Label.pack()

    def get_assigned_device(self, searchIP):
        """
        対象IPがインターフェイスに設定されているデバイスを抽出する関数

        :param searchIP: 検索対象IP

        :return: 対象IPがインターフェイスに設定されているデバイスクラス
        """
        for Device in self.Devices:
            if Device.is_ip_assigned(searchIP):
                return Device
        return None

    def search_first_device(self, first_device, searchIP):
        """
        通信経路を探索する最初のデバイスを検索する関数

        :param first_device: ユーザーが選択したデバイス
        :param searchIP: 検索対象となるIP

        :return: 通信経路の元となるデバイスクラス

        """
        TTL = 255
        Device = self.get_assigned_device(searchIP)
        if not Device is None:
            return Device

        before_device = first_device
        for i in range(TTL):
            nexthop_IPs, _ = before_device.find_nexthop(searchIP)
            if nexthop_IPs:
                next_device = self.get_assigned_device(nexthop_IPs[0])
                if next_device is None:
                    return before_device
                before_device = next_device
            else:
                return before_device
        return None

    def TraceIP(self, Device, searchIP, path, result):
        """
        入力されたIPから通信経路を計算する巻子う

        :param Device: 検索対象となるデバイスクラス
        :param searchIP: 検索対象IP
        :param path: 計算過程の通信経路
        :param result: 探索が完了した通信経路を格納する配列

        :return result: 探索が完了した通信経路を格納した配列
        """
        if Device == None:
            result.append(copy.deepcopy(path))
            return
        nexthop_IPs, nexthop_IFs = Device.find_nexthop(searchIP)

        if not nexthop_IPs:
            path["nexthopIF"].append(safe_get_element(nexthop_IFs, 0, ""))
            result.append(copy.deepcopy(path))
            return

        for i in range(len(nexthop_IPs)):
            path["nexthopIF"].append(safe_get_element(nexthop_IFs, i, ""))
            nextDevice = None
            for targetDevice in self.Devices:
                if targetDevice.is_ip_assigned(nexthop_IPs[i]):
                    nextDevice = targetDevice
                    receiveIF = nextDevice.find_local_IF(nexthop_IPs[i])
                    path["Device"].append(nextDevice)
                    path["receiveIF"].append(receiveIF)
                    break
            self.TraceIP(nextDevice, searchIP, copy.deepcopy(path), result)
            path["receiveIF"].pop()
            path["Device"].pop()
            path["nexthopIF"].pop()

    def calcPath(self, paths):
        textPath = ""
        for path in paths:
            textPath += self.SourceIP_Entry.get() + " → "
            for i in range(len(path["receiveIF"])):
                textPath += "(" + path["receiveIF"][i] + ")" + path["Device"][i].get_name() + "(" + path["nexthopIF"][i] + ")" + " → "
            textPath += self.DestinationIP_Entry.get() + "\n"
        return textPath

    def searchRoute(self):
        search_sourceIP = self.SourceIP_Entry.get()
        search_destinationIP = self.DestinationIP_Entry.get()

        if not (search_sourceIP or search_destinationIP):
            return

        self.Caution_Label["text"] = ""

        selectDeviceName = self.selectDevice.get()

        if not selectDeviceName:
            self.Caution_Label["text"] = "検索対象のデバイスを選択してください"
            return

        for Device in self.Devices:
            if Device.get_name() == selectDeviceName:
                selectDevice = Device

        Device = self.search_first_device(selectDevice, search_sourceIP)
        _, receiveIFs = Device.find_nexthop(search_sourceIP)
        receiveIF = receiveIFs[0]

        path_temp = {"receiveIF":[receiveIF], "Device":[Device], "nexthopIF":[]}
        results = list()
        self.TraceIP(Device, search_destinationIP, path_temp, results)

        text = self.calcPath(results)
        self.Result_Label["text"] = text



def safe_get_element(my_list, index, default_value=None):
    """
    リストから要素を安全に取り出す関数

    :param my_list: 対象のリスト
    :param index: 取り出す要素のインデックス
    :param default_value: インデックスが範囲外の場合に返すデフォルト値 (デフォルトはNone)
    :return: インデックスが範囲内の場合はリストの要素、範囲外の場合はデフォルト値
    """
    try:
        result = my_list[index]
    except IndexError:
        result = default_value
    return result


#デバイスのルート情報を抽出
def extract_route_info(file_path, template_path, device_type):
    """
    デバイスのルーティングテーブルを取り出す関数

    :param file_path: 対象デバイスのパス
    :param tempalte_path: textfsmファイルのパス
    :param device_type: デバイスのタイプ
    :return: ルーティング情報を保持したデバイスクラス
    """
    device_name = os.path.basename(file_path).split('.')[0]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            conf = f.read()
        with open(template_path, 'r', encoding='utf-8') as ftemplate:
            fsm = textfsm.TextFSM(ftemplate)
            if device_type == "asa":
                return ASA(device_name, conf, fsm)
            elif device_type == "ios":
                return IOS(device_name, conf, fsm)
            elif device_type == "nxos":
                return NXOS(device_name, conf, fsm)
            elif device_type == "virtual":
                return VIRTUAL(device_name, conf, fsm)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return {}

def get_device_route(device_types, templates):
    # デバイスのルート情報を抽出して辞書に格納
    Devices = list()
    for device_type, file_pattern in device_types.items():
        files = glob.glob(file_pattern)
        template_path = templates[device_type]
        for file in files:
            Devices.append(extract_route_info(file, template_path, device_type))
    return Devices

def main():
    Devices = list()
    device_types = {"asa": "./config/asa/*.txt",
                    "ios": "./config/ios/*.txt",
                    "nxos": "./config/nxos/*.txt",
                    "virtual": "./config/virtual/*.txt"}
    templates = {"asa": "./templates/cisco_asa_show_route.textfsm",
                 "ios": "./templates/cisco_ios_show_ip_route.textfsm",
                 "nxos": "./templates/cisco_nxos_show_ip_route.textfsm",
                 "virtual": "./templates/virtual_route.textfsm"}

    Devices = get_device_route(device_types, templates)

    root = tk.Tk()
    app = Application(master=root, Devices=Devices)
    app.mainloop()



if __name__ == "__main__":
    main()
