import ipaddress
from abc import ABC, abstractmethod
import logging
from logging import getLogger, StreamHandler, Formatter

class Device(ABC):

    # 初期化メソッド
    def __init__(self, name, config, textFSM):
        self.name = name
        self.all_routes = self.extract_route_info(config, textFSM)

    def get_name(self):
        return self.name

    def extract_route_info(self, config, textFSM):
        return [dict(zip(textFSM.header, item)) for item in textFSM.ParseText(config)]

    @staticmethod
    def prefix_to_subnet_mask(prefix):
        try:
            network = ipaddress.IPv4Network(f'0.0.0.0/{prefix}', strict=False)
            return str(network.netmask)
        except ValueError:
            return "Invalid prefix"

    # connected_routeを抜き出す
    @abstractmethod
    def get_local_routes(self):
        pass

    @abstractmethod
    def get_connected_routes(self):
        pass

    @abstractmethod
    def extract_local_routes(self):
        pass

    @abstractmethod
    def extract_connected_routes(self):
        pass

    # 入力されたIPをデバイスのIFが持っているか
    @abstractmethod
    def is_ip_assigned(self, ip_address, netmask=32):
        pass

    # 入力されたIPをデバイスがConnectedで持っているか
    @abstractmethod
    def is_ip_connected(self, ip_address, netmask=32):
        pass

    @abstractmethod
    def find_local_IF(self, ip_address):
        pass

    # 入力されたIPアドレスに対してnexthop, nexthop_IFを検索するためのコードを実装
    @abstractmethod
    def find_nexthop(self, ip_address):
        pass
