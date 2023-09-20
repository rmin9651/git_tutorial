from service_parse import *
import unittest

class TestService(unittest.TestCase):

    def test_known_port(self):
        # 既知のポート番号を正しく変換するか確認
        port = "http"
        converted_port = port_change(port)
        self.assertEqual(converted_port, "80")

    def test_unknown_port(self):
        # 未知のポート番号は変換しないことを確認
        port = "unknown"
        converted_port = port_change(port)
        self.assertEqual(converted_port, "unknown")
class TestProtocolJudge(unittest.TestCase):

    def test_matching_protocol(self):
        self.assertTrue(protocol_judge("tcp", "tcp"))
        self.assertTrue(protocol_judge("icmp", "icmp"))

    def test_non_matching_protocol(self):
        self.assertFalse(protocol_judge("udp", "tcp"))
        self.assertFalse(protocol_judge("icmp", "tcp"))

    def test_tcp_udp_protocol(self):
        self.assertTrue(protocol_judge("tcp", "tcp-udp"))
        self.assertTrue(protocol_judge("udp", "tcp-udp"))

    def test_any_protocol(self):
        self.assertTrue(protocol_judge("tcp", "any"))
        self.assertTrue(protocol_judge("udp", "any"))
        self.assertTrue(protocol_judge("icmp", "any"))
        self.assertTrue(protocol_judge("tcp-udp", "any"))

class TestPortJudge(unittest.TestCase):

    def test_eq_operator(self):
        self.assertTrue(port_judge("80", "80", "eq"))

    def test_gt_operator(self):
        self.assertTrue(port_judge("8080", "80", "gt"))

    def test_lt_operator(self):
        self.assertTrue(port_judge("80", "8080", "lt"))

    def test_range_operator(self):
        self.assertTrue(port_judge("8080", "8000-8100", "range"))

    def test_invalid_operator(self):
        self.assertFalse(port_judge("80", "8080", "invalid"))

    def test_any_port(self):
        self.assertTrue(port_judge("80", "any", "eq"))

class TestSrvJudge(unittest.TestCase):

    def test_matching_srv(self):
        srv = {"protocol": "tcp", "src_port": "80", "src_ope": "eq", "dst_port": "80", "dst_ope": "eq"}
        self.assertTrue(srv_judge("tcp", "80", srv))

    def test_non_matching_srv(self):
        srv = {"protocol": "tcp", "src_port": "80", "src_ope": "eq", "dst_port": "8080", "dst_ope": "eq"}
        self.assertFalse(srv_judge("tcp", "80", srv))

class TestSrvsJudge(unittest.TestCase):

    def test_matching_srvs(self):
        srvs = [
            {"protocol": "tcp", "src_port": "80", "src_ope": "eq", "dst_port": "80", "dst_ope": "eq"},
            {"protocol": "udp", "src_port": "53", "src_ope": "eq", "dst_port": "53", "dst_ope": "eq"},
        ]
        self.assertTrue(srvs_judge("tcp", "80", srvs))
        self.assertTrue(srvs_judge("udp", "53", srvs))

    def test_non_matching_srvs(self):
        srvs = [
            {"protocol": "tcp", "src_port": "80", "src_ope": "eq", "dst_port": "8080", "dst_ope": "eq"},
            {"protocol": "udp", "src_port": "53", "src_ope": "eq", "dst_port": "8080", "dst_ope": "eq"},
        ]
        self.assertFalse(srvs_judge("tcp", "80", srvs))
        self.assertFalse(srvs_judge("udp", "53", srvs))

class TestSrvsMultiJudge(unittest.TestCase):

    def test_matching_ports_protocols(self):
        target_ports_protocols = ["80/tcp", "53/udp"]
        srvs = [
            {"protocol": "tcp", "src_port": "80", "src_ope": "eq", "dst_port": "80", "dst_ope": "eq"},
            {"protocol": "udp", "src_port": "53", "src_ope": "eq", "dst_port": "53", "dst_ope": "eq"},
        ]
        self.assertTrue(srvs_multi_judge(target_ports_protocols, srvs))

    def test_non_matching_ports_protocols(self):
        target_ports_protocols = ["80/tcp", "53/udp"]
        srvs = [
            {"protocol": "tcp", "src_port": "80", "src_ope": "eq", "dst_port": "8080", "dst_ope": "eq"},
            {"protocol": "udp", "src_port": "53", "src_ope": "eq", "dst_port": "8080", "dst_ope": "eq"},
        ]
        self.assertFalse(srvs_multi_judge(target_ports_protocols, srvs))

class TestIsValidPortProtocol(unittest.TestCase):

    def test_valid_port_protocol(self):
        self.assertTrue(is_valid_port_protocol("80/tcp"))

    def test_invalid_port_protocol(self):
        self.assertFalse(is_valid_port_protocol("80/invalid"))
        self.assertFalse(is_valid_port_protocol("80-tcp"))

class TestIsValidPortsProtocols(unittest.TestCase):

    def test_valid_ports_protocols(self):
        self.assertTrue(is_valid_ports_protocols(["80/tcp", "53/udp"]))

    def test_invalid_ports_protocols(self):
        self.assertFalse(is_valid_ports_protocols(["80/tcp", "53/invalid"]))
        self.assertFalse(is_valid_ports_protocols(["80-tcp", "53/udp"]))

class TestServiceFunctions(unittest.TestCase):

    def test_update_group_members(self):
        srv = {
            "grp": {
                "group1": [
                    {"TYPE": "group", "GRP_OBJECT": "group2"},
                    {"TYPE": "object", "PROTOCOL": "tcp"},
                ],
                "group2": [
                    {"TYPE": "object", "PROTOCOL": "udp"},
                ]
            }
        }

        update_group_members(srv)

        # group1のメンバーにgroup2のメンバーが追加されているかを確認
        self.assertEqual(len(srv["grp"]["group1"]), 2)
        self.assertEqual(srv["grp"]["group1"][1]["PROTOCOL"], "udp")

    def test_process_service_data(self):
        data = {
            "PROTOCOL": "tcp",
            "DST_PORT": "80",
            "DST_PORT_RANGE_START": "",
            "DST_PORT_RANGE_END": "",
            "DST_PORT_LESS_THAN": "",
            "DST_PORT_GREATER_THAN": "",
            "PORT_OBJECT": "",
            "PORT_OBJECT_START": "",
            "PORT_OBJECT_END": "",
            "SRC_PORT": "1024",
            "SRC_PORT_RANGE_START": "",
            "SRC_PORT_RANGE_END": "",
            "SRC_PORT_LESS_THAN": "",
            "SRC_PORT_GREATER_THAN": "",
            "PORT_OBJECT": "",
            "PORT_OBJECT_START": "",
            "PORT_OBJECT_END": ""
        }

        result = process_service_data(data)
        expected_result = {"protocol":"tcp", "src_ope":"eq", "src_port":"1024", "dst_ope":"eq", "dst_port":"80"}

        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
