from Device import Device
import ipaddress

class IOS(Device):

    #初期化メソッド
    def __init__(self, name, config, textFSM):
        super().__init__(name, config, textFSM)
        self.connected_routes = self.extract_connected_routes(self.all_routes)
        self.local_routes = self.extract_local_routes(self.all_routes)

    def get_local_routes(self):
        return self.local_routes

    def get_connected_routes(self):
        return self.connected_routes

    def get_all_routes(self):
        return self.all_routes

    #入力されたIPをデバイスが直接持っているか
    def is_ip_assigned(self, ip_address, netmask="32"):
        Flag = False
        for route in self.local_routes:
            if ipaddress.IPv4Network(route["NETWORK"] + "/" + route["PREFIX_LENGTH"]) == ipaddress.IPv4Network(ip_address + "/" + netmask):
                Flag = True
                break
        return Flag

    #入力されたIPをデバイスがConnectedで持っているか
    def is_ip_connected(self, ip_address, netmask="32"):
        Flag = False
        for route in self.connected_routes:
            if ipaddress.IPv4Network(route["NETWORK"] + "/" + route["PREFIX_LENGTH"]) == ipaddress.IPv4Network(ip_address + "/" + netmask):
                Flag = True
                break
        return Flag

    #直接接続されているrouteを抜き出す
    def extract_connected_routes(self, all_routes):
        connected_routes = list()
        for route in self.all_routes:
            if route["PROTOCOL"] == "C":
                connected_routes.append(route)
        return connected_routes

    #connected_routeを抜き出す
    def extract_local_routes(self, all_routes):
        local_routes = list()
        for route in self.all_routes:
            if route["PROTOCOL"] == "L":
                local_routes.append(route)
        return local_routes

    #入力されたIPアドレスが設定されているIFを検索
    def find_local_IF(self, ip_address):
        IF = None
        for route in self.local_routes:
            if ipaddress.IPv4Address(route["NETWORK"]) == ipaddress.IPv4Address(ip_address):
                IF = route["NEXTHOP_IF"]
                break
        return IF

    #入力されたIPアドレスに対してnexthop, nexthop_IFを検索するためのコードを実装
    def find_nexthop(self, ip_address):
        match_route = list()
        ip_address = ipaddress.IPv4Address(ip_address)
        for route in self.all_routes:
            network = ipaddress.IPv4Network(route["NETWORK"] + "/" + route["PREFIX_LENGTH"], strict=False)
            if ip_address in network:
                match_route.append(route)
        nexthop_IPs = list()
        nexthop_IFs = list()
        for prefix in range(32, -1, -1):
            for route in match_route:
                if route["PREFIX_LENGTH"] == str(prefix):
                    if not route["NEXTHOP_IP"] == "":
                        nexthop_IPs.append(route["NEXTHOP_IP"])
                    if not route["NEXTHOP_IF"] == "":
                        nexthop_IFs.append(route["NEXTHOP_IF"])
            if nexthop_IPs or nexthop_IFs:
                return nexthop_IPs, nexthop_IFs
        return None, None
