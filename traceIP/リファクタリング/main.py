from ASA import ASA
from IOS import IOS
from NXOS import NXOS
import textfsm
import glob
import os
import copy
from pprint import pprint


def extract_route_info(file_path, template_path, device_type):
    Devices = list()
    device_name = os.path.basename(file_path).split('.')[0]
    try:
        with open(file_path) as f:
            conf = f.read()
        with open(template_path) as ftemplate:
            fsm = textfsm.TextFSM(ftemplate)
            if device_type == "asa":
                return ASA(device_name, conf, fsm)
            if device_type == "ios":
                return IOS(device_name, conf, fsm)
            if device_type == "nxos":
                return NXOS(device_name, conf, fsm)
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

def TraceIP(Device, Devices, searchIP, path, result):
    if Device == None:
        return
    nexthop_IPs, nexthop_IFs = Device.find_nexthop(searchIP)

    if not nexthop_IPs:
        path["nexthopIF"].append(nexthop_IFs[0])
        result.append(copy.deepcopy(path))
        return

    for i in range(len(nexthop_IPs)):
        path["nexthopIF"].append(nexthop_IFs[i])
        nextDevice = None
        for targetDevice in Devices:
            if targetDevice.is_ip_assigned(nexthop_IPs[i]):
                nextDevice = targetDevice
                receiveIF = nextDevice.find_local_IF(nexthop_IPs[i])
                path["Device"].append(nextDevice)
                path["receiveIF"].append(receiveIF)
        TraceIP(nextDevice, Devices, searchIP, copy.deepcopy(path), result)
        path["receiveIF"].pop()
        path["Device"].pop()
        path["nexthopIF"].pop()

def main():
    Devices = list()
    device_types = {"asa": "./config/asa/*.txt", "ios": "./config/ios/*.txt", "nxos": "./config/nxos/*.txt"}
    templates = {"asa": "./templates/cisco_asa_show_route.textfsm",
                 "ios": "./templates/cisco_ios_show_ip_route.textfsm",
                 "nxos": "./templates/cisco_nxos_show_ip_route.textfsm"}

    Devices = get_device_route(device_types, templates)

    Device = Devices[7]
    path_temp = {"receiveIF":["inside1"], "Device":[Device], "nexthopIF":[]}
    result = list()
    TraceIP(Device, Devices, "10.0.1.0", path_temp, result)

    for paths in result:
        for i in range(len(paths["receiveIF"])):
            print( "(" + paths["receiveIF"][i] + ")" + paths["Device"][i].get_name() + "(" + paths["nexthopIF"][i] + ")", end=" → ")
        print()


if __name__ == "__main__":
    main()
