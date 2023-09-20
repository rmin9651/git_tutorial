import unittest
import ipaddress  # prefix_to_subnet_mask 関数で使用するためにインポート
from network_parse import *

class TestNetworkConversionFunctions(unittest.TestCase):

    def test_mask_or_prefix_to_prefix_with_prefix(self):
        # プレフィックスが入力された場合はそのまま返すテスト
        input_value = "/24"
        result = mask_or_prefix_to_prefix(input_value)
        self.assertEqual(result, input_value)

    def test_mask_or_prefix_to_prefix_with_subnet_mask(self):
        # サブネットマスクが正しい場合に変換して返すテスト
        input_value = "255.255.255.0"
        result = mask_or_prefix_to_prefix(input_value)
        self.assertEqual(result, "/24")

    def test_mask_or_prefix_to_prefix_with_invalid_subnet_mask(self):
        # 不正なサブネットマスクが入力された場合にエラーメッセージを返すテスト
        input_value = "256.0.0.0"
        result = mask_or_prefix_to_prefix(input_value)
        self.assertEqual(result, "Invalid subnet mask")

    def test_prefix_to_subnet_mask_with_valid_prefix(self):
        # 有効なプレフィックスが入力された場合にサブネットマスクを返すテスト
        prefix = "24"
        result = prefix_to_subnet_mask(prefix)
        self.assertEqual(result, "255.255.255.0")

    def test_prefix_to_subnet_mask_with_invalid_prefix(self):
        # 不正なプレフィックスが入力された場合にエラーメッセージを返すテスト
        prefix = "33"  # 33は無効なプレフィックス長
        result = prefix_to_subnet_mask(prefix)
        self.assertEqual(result, "Invalid prefix")

class TestNetworkValidFunctions(unittest.TestCase):
    def test_is_ipv4_or_network_address_with_valid_ipv4(self):
        # 有効なIPv4アドレスが正しく認識されることをテスト
        input_str = "192.168.1.1"
        result = is_ipv4_or_network_address(input_str)
        self.assertTrue(result)

    def test_is_ipv4_or_network_address_with_valid_network_address(self):
        # 有効なCIDR表記のネットワークアドレスが正しく認識されることをテスト
        input_str = "192.168.1.0/24"
        result = is_ipv4_or_network_address(input_str)
        self.assertTrue(result)

    def test_is_ipv4_or_network_address_with_invalid_address(self):
        # 無効なアドレスが正しく認識されることをテスト
        input_str = "invalid_address"
        result = is_ipv4_or_network_address(input_str)
        self.assertFalse(result)

    def test_summarize_ip_range_valid(self):
        # 有効な IP アドレス範囲のテスト
        start_ip = "192.168.1.5"
        end_ip = "192.168.1.10"
        summarized_networks = summarize_ip_range(start_ip, end_ip)
        expected_result = [ipaddress.IPv4Network('192.168.1.5/32'), ipaddress.IPv4Network('192.168.1.6/31'), ipaddress.IPv4Network('192.168.1.8/31'), ipaddress.IPv4Network('192.168.1.10/32')]
        self.assertEqual(summarized_networks, expected_result)

    def test_is_ipv4_or_network_addresses_with_valid_addresses(self):
        # 有効なアドレスリストがすべて正しく認識されることをテスト
        input_str = ["192.168.1.1", "10.0.0.0/16", "172.16.0.0/12"]
        result = is_ipv4_or_network_addresses(input_str)
        self.assertTrue(result)

    def test_is_ipv4_or_network_addresses_with_invalid_addresses(self):
        # 無効なアドレスが含まれるリストが正しく認識されることをテスト
        input_str = ["192.168.1.1", "invalid_address", "10.0.0.0/16"]
        result = is_ipv4_or_network_addresses(input_str)
        self.assertFalse(result)

class TestNetworkJudgeFunctions(unittest.TestCase):
    def test_summarize_ip_range_single_ip(self):
        # 単一の IP アドレスのテスト
        start_ip = "192.168.1.5"
        end_ip = "192.168.1.5"
        summarized_networks = summarize_ip_range(start_ip, end_ip)
        expected_result = [ipaddress.IPv4Network("192.168.1.5/32")]
        self.assertEqual(summarized_networks, expected_result)

    def test_summarize_ip_range_invalid_range(self):
        # 無効な IP アドレス範囲のテスト（開始 IP > 終了 IP）
        start_ip = "192.168.1.10"
        end_ip = "192.168.1.5"
        summarized_networks = summarize_ip_range(start_ip, end_ip)
        expected_result = []
        self.assertEqual(summarized_networks, expected_result)

    def test_check_ip_in_range_valid_ip(self):
        # 有効なIPが範囲内にある場合のテスト
        target_ip = "192.168.1.5"
        start_ip = "192.168.1.1"
        end_ip = "192.168.1.10"
        result = check_ip_in_range(target_ip, start_ip, end_ip)
        self.assertTrue(result)

    def test_check_ip_in_range_invalid_ip(self):
        # 無効なIPが範囲内にある場合のテスト
        target_ip = "192.168.1.5"
        start_ip = "192.168.1.10"
        end_ip = "192.168.1.20"
        result = check_ip_in_range(target_ip, start_ip, end_ip)
        self.assertFalse(result)

    def test_check_ip_in_network_valid_ip(self):
        # 有効なIPがネットワークに含まれる場合のテスト
        target_ip = "192.168.1.5"
        network = "192.168.1.0/24"
        result = check_ip_in_network(target_ip, network)
        self.assertTrue(result)

    def test_check_ip_in_network_invalid_ip(self):
        # 無効なIPがネットワークに含まれる場合のテスト
        target_ip = "192.168.2.5"
        network = "192.168.1.0/24"
        result = check_ip_in_network(target_ip, network)
        self.assertFalse(result)

    def test_check_ip_equal_valid_ip(self):
        # 有効なIPが等しい場合のテスト
        target_ip = "192.168.1.5"
        reference_ip = "192.168.1.5"
        result = check_ip_equal(target_ip, reference_ip)
        self.assertTrue(result)

    def test_check_ip_equal_invalid_ip(self):
        # 無効なIPが等しい場合のテスト
        target_ip = "192.168.1.5"
        reference_ip = "192.168.1.6"
        result = check_ip_equal(target_ip, reference_ip)
        self.assertFalse(result)

    def test_check_network_in_network_subnet_valid(self):
        # ネットワークがサブネット内にある場合のテスト
        target_network = "192.168.0.0/16"
        reference_ip = "192.168.0.0/24"
        result = check_network_in_network_subnet(target_network, reference_ip)
        self.assertTrue(result)

    def test_check_network_in_network_subnet_invalid(self):
        # ネットワークがサブネット外にある場合のテスト
        target_network = "192.168.0.0/24"
        reference_ip = "192.168.1.0/24"
        result = check_network_in_network_subnet(target_network, reference_ip)
        self.assertFalse(result)

    def test_check_range_in_network_subnet_valid(self):
        # IPアドレス範囲がネットワークのサブネット内にある場合のテスト
        target_network = "192.168.0.0/24"
        start_ip = "192.168.0.5"
        end_ip = "192.168.0.10"
        result = check_range_in_network_subnet(target_network, start_ip, end_ip)
        self.assertTrue(result)

    def test_check_range_in_network_subnet_invalid(self):
        # IPアドレス範囲がネットワークのサブネット外にある場合のテスト
        target_network = "192.168.0.0/24"
        start_ip = "192.168.1.5"
        end_ip = "192.168.1.10"
        result = check_range_in_network_subnet(target_network, start_ip, end_ip)
        self.assertFalse(result)

    def test_ip_match_valid(self):
        # IPアドレスが一致する場合のテスト
        target_ip = "192.168.1.5"
        reference_ip = "192.168.1.5"
        reference_type = "host"
        result = ip_match(target_ip, reference_ip, reference_type)
        self.assertTrue(result)

    def test_ip_match_invalid(self):
        # IPアドレスが一致しない場合のテスト
        target_ip = "192.168.1.5"
        reference_ip = "192.168.1.6"
        reference_type = "host"
        result = ip_match(target_ip, reference_ip, reference_type)
        self.assertFalse(result)

    def test_ip_matchs_valid(self):
        # 複数のIPアドレスが一致する場合のテスト
        target_ip = "192.168.1.5"
        reference_ips = [{"ip": "192.168.1.5", "type": "host"}, {"ip": "192.168.1.6", "type": "host"}]
        result = ip_matchs(target_ip, reference_ips)
        self.assertTrue(result)

    def test_ip_matchs_invalid(self):
        # 複数のIPアドレスが一致しない場合のテスト
        target_ip = "192.168.1.5"
        reference_ips = [{"ip": "192.168.1.6", "type": "host"}, {"ip": "10.0.0.1", "type": "host"}]
        result = ip_matchs(target_ip, reference_ips)
        self.assertFalse(result)

    def test_network_match_valid(self):
        # ネットワークが一致する場合のテスト
        target_network = "192.168.0.0/24"
        reference_ip = "192.168.0.0/24"
        reference_type = "network"
        result = network_match(target_network, reference_ip, reference_type)
        self.assertTrue(result)

    def test_network_match_invalid(self):
        # ネットワークが一致しない場合のテスト
        target_network = "192.168.0.0/24"
        reference_ip = "192.168.1.0/24"
        reference_type = "network"
        result = network_match(target_network, reference_ip, reference_type)
        self.assertFalse(result)

    def test_network_matchs_valid(self):
        # 複数のネットワークが一致する場合のテスト
        target_network = "192.168.0.0/24"
        reference_ips = [{"ip": "192.168.0.0/24", "type": "network"}, {"ip": "192.168.1.0/24", "type": "network"}]
        result = network_matchs(target_network, reference_ips)
        self.assertTrue(result)

    def test_network_matchs_invalid(self):
        # 複数のネットワークが一致しない場合のテスト
        target_network = "192.168.0.0/24"
        reference_ips = [{"ip": "192.168.1.0/24", "type": "network"}, {"ip": "10.0.0.0/24", "type": "network"}]
        result = network_matchs(target_network, reference_ips)
        self.assertFalse(result)

    def test_ips_matchs_valid(self):
        # 複数のIPアドレスとネットワークがすべて一致する場合のテスト
        target_ips = ["192.168.1.5", "10.0.0.1", "192.168.0.0/24"]
        reference_ips = [
            {"ip": "192.168.1.5", "type": "host"},
            {"ip": "10.0.0.1", "type": "host"},
            {"ip": "192.168.0.0/24", "type": "network"}
        ]
        result = ips_matchs(target_ips, reference_ips)
        self.assertTrue(result)

    def test_ips_matchs_invalid(self):
        # 複数のIPアドレスとネットワークがすべて一致しない場合のテスト
        target_ips = ["192.168.1.5", "10.0.0.1", "192.168.2.0/24"]
        reference_ips = [
            {"ip": "192.168.1.6", "type": "host"},
            {"ip": "10.0.0.2", "type": "host"},
            {"ip": "192.168.1.0/24", "type": "network"}
        ]
        result = ips_matchs(target_ips, reference_ips)
        self.assertFalse(result)


class TestNetworkProcessFunctions(unittest.TestCase):
    def test_process_network_data_host(self):
        # ホストタイプのネットワークデータを正しく処理するか確認
        data = {"HOST": "192.168.1.1", "NETWORK": "", "NETMASK": "", "PREFIX_LENGTH": "", "START_IP": "", "END_IP": ""}
        processed_data = process_network_data(data)
        expected_result = {"type": "host", "ip": "192.168.1.1"}
        self.assertEqual(processed_data, expected_result)

    def test_process_network_data_network(self):
        # ネットワークタイプのネットワークデータを正しく処理するか確認
        data = {"HOST": "", "NETWORK": "192.168.1.0", "NETMASK": "255.255.255.0", "PREFIX_LENGTH": "", "START_IP": "", "END_IP": ""}
        processed_data = process_network_data(data)
        expected_result = {"type": "network", "ip": "192.168.1.0/24"}
        self.assertEqual(processed_data, expected_result)

    def test_process_network_data_range(self):
        # レンジタイプのネットワークデータを正しく処理するか確認
        data = {"HOST": "", "NETWORK": "", "NETMASK": "", "PREFIX_LENGTH": "", "START_IP": "192.168.1.1", "END_IP": "192.168.1.10"}
        processed_data = process_network_data(data)
        expected_result = {"type": "range", "ip": "192.168.1.1-192.168.1.10"}
        self.assertEqual(processed_data, expected_result)

    def test_update_group_members(self):
        # グループメンバーの更新を正しく行うか確認
        ntw = {
            "grp": {
                "Group1": [
                    {"TYPE": "group", "GRP_OBJECT": "Group2"},
                    {"TYPE": "object", "NET_OBJECT": "Object1"}
                ],
                "Group2": [
                    {"TYPE": "object", "NET_OBJECT": "Object2"}
                ]
            },
            "obj": {
                "Object1": [{"type": "host", "ip": "192.168.1.1"}],
                "Object2": [{"type": "network", "ip": "192.168.2.0/24"}]
            }
        }

        update_group_members(ntw)

        expected_result = {
            "grp": {
                "Group1":  [{'ip': '192.168.1.1', 'type': 'host'},
                            {'ip': '192.168.2.0/24', 'type': 'network'}],
                "Group2": [{'ip': '192.168.2.0/24', 'type': 'network'}]
            },
            "obj": {
                "Object1": [{"ip": "192.168.1.1", "type": "host"}],
                "Object2": [{"ip": "192.168.2.0/24", "type": "network"}]
            }
        }

        self.assertEqual(ntw, expected_result)

if __name__ == '__main__':
    unittest.main()
