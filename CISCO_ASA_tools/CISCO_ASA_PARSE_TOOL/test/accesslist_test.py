import unittest
from access_list_parse import *

class TestAccesslistFunctions(unittest.TestCase):
    def test_port_eq_summary(self):
        # port_summary eq関数のテスト
        accesslist_data = {
            "DST_PORT": "80",
            "DST_PORT_GREATER_THAN": "",
            "DST_PORT_LESS_THAN": "",
            "DST_PORT_RANGE_START": "",
            "DST_PORT_RANGE_END": "",
            "DST_PORT_GRP": "",
        }
        service_data = {}
        expected_result = [{"protocol": "any", "src_ope": "any", "src_port": "any", "dst_ope": "eq", "dst_port": "80"}]
        result = port_summary(accesslist_data, service_data)
        self.assertEqual(result, expected_result)

    def test_port_gt_summary(self):
        # port_summary gt関数のテスト
        accesslist_data = {
            "DST_PORT": "",
            "DST_PORT_GREATER_THAN": "443",
            "DST_PORT_LESS_THAN": "",
            "DST_PORT_RANGE_START": "",
            "DST_PORT_RANGE_END": "",
            "DST_PORT_GRP": "",
        }
        service_data = {}
        expected_result = [{"protocol": "any", "src_ope": "any", "src_port": "any", "dst_ope": "gt", "dst_port": "443"}]
        result = port_summary(accesslist_data, service_data)
        self.assertEqual(result, expected_result)

    def test_port_lt_summary(self):
        # port_summary lt関数のテスト
        accesslist_data = {
            "DST_PORT": "",
            "DST_PORT_GREATER_THAN": "",
            "DST_PORT_LESS_THAN": "www",
            "DST_PORT_RANGE_START": "",
            "DST_PORT_RANGE_END": "",
            "DST_PORT_GRP": "",
        }
        service_data = {}
        expected_result = [{"protocol": "any", "src_ope": "any", "src_port": "any", "dst_ope": "lt", "dst_port": "443"}]
        result = port_summary(accesslist_data, service_data)
        self.assertEqual(result, expected_result)

    def test_port_lt_summary(self):
        # port_summary range 関数のテスト
        accesslist_data = {
            "DST_PORT": "",
            "DST_PORT_GREATER_THAN": "",
            "DST_PORT_LESS_THAN": "",
            "DST_PORT_RANGE_START": "80",
            "DST_PORT_RANGE_END": "443",
            "DST_PORT_GRP": "",
        }
        service_data = {}
        expected_result = [{"protocol": "any", "src_ope": "any", "src_port": "any", "dst_ope": "range", "dst_port": "80-443"}]
        result = port_summary(accesslist_data, service_data)
        self.assertEqual(result, expected_result)

    def test_port_group_summary(self):
        # port_summary group 関数のテスト
        accesslist_data = {
            "DST_PORT": "",
            "DST_PORT_GREATER_THAN": "",
            "DST_PORT_LESS_THAN": "",
            "DST_PORT_RANGE_START": "",
            "DST_PORT_RANGE_END": "",
            "DST_PORT_GRP": "Test",
        }
        service_data = {
            "grp":{
                "Test":[
                    {"protocol": "any", "src_ope": "eq", "src_port": "80", "dst_ope": "eq", "dst_port": "80"}
                ]
            }
        }
        expected_result = [{"protocol": "any", "src_ope": "eq", "src_port": "80", "dst_ope": "eq", "dst_port": "80"}]
        result = port_summary(accesslist_data, service_data)
        self.assertEqual(result, expected_result)

    def test_protocol_port_merge(self):
        # protocol_port_merge 関数のテスト
        protocol_group = [
            {"protocol": "tcp", "src_ope": "any", "src_port": "any", "dst_ope": "any", "dst_port": "any"},
            {"protocol": "udp", "src_ope": "any", "src_port": "any", "dst_ope": "any", "dst_port": "any"}
        ]
        port_group = [
            {"protocol": "any", "src_ope": "any", "src_port": "any", "dst_ope": "eq", "dst_port": "80"},
            {"protocol": "any", "src_ope": "any", "src_port": "any", "dst_ope": "eq", "dst_port": "443"}
        ]
        expected_result = [
            {"protocol": "tcp", "src_ope": "any", "src_port": "any", "dst_ope": "eq", "dst_port": "80"},
            {"protocol": "tcp", "src_ope": "any", "src_port": "any", "dst_ope": "eq", "dst_port": "443"},
            {"protocol": "udp", "src_ope": "any", "src_port": "any", "dst_ope": "eq", "dst_port": "80"},
            {"protocol": "udp", "src_ope": "any", "src_port": "any", "dst_ope": "eq", "dst_port": "443"},
        ]
        result = protocol_port_merge(protocol_group, port_group)
        self.assertEqual(result, expected_result)


    # 他の関数のテストケースも同様に作成

if __name__ == '__main__':
    unittest.main()
