import networkx as nx #networkxのインポート
import ipaddress
class NWGraph:

    allDeviceNode = list()
    allConnectedNode = list()
    node_size = list()

    def __init__(self, Devices):
        self.G = nx.Graph()
        self.addAllNode(Devices)
        self.addDeviceEdge()

    def addAllNode(self, Devices):
        self.addDeviceNode(Devices)
        self.addConnectedNode(Devices)
        self.setNodeSide()

    #デバイスノードの追加
    def addDeviceNode(self, Devices):
        self.allDeviceNode = Devices
        for Device in Devices:
            self.G.add_node(Device.get_name())

    #connectedノードの追加
    def addConnectedNode(self, Devices):
        for Device in Devices:
            for connectedRoute in Device.get_connected_routes():
                route = ipaddress.IPv4Network(connectedRoute["NETWORK"] + "/" + (connectedRoute.get("NETMASK", "") + connectedRoute.get("PREFIX_LENGTH", "")), strict=False)
                self.allConnectedNode.append(route)
                self.G.add_node(str(route))

    #デバイスとConnnecteRouteを接続
    def addDeviceEdge(self):
        for connectedRoute in self.allConnectedNode:
            for Device in self.allDeviceNode:
                if Device.is_ip_connected(str(connectedRoute.network_address), str(connectedRoute.prefixlen)):
                    self.G.add_edge(Device.get_name(), str(connectedRoute))

    def exitDeviceName(self, node):
        for Device in self.allDeviceNode:
            if Device.get_name() == node:
                return True
        return False

    def setNodeSide(self):
        self.node_size = [100 if self.exitDeviceName(node) else 1 for (node,d) in self.G.nodes(data=True)]
