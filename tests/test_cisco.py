import json
import os
import unittest
from mydict import MyDict
from unittest.mock import patch, MagicMock
from network_automation.cisco import CiscoSSHDevice

current_dir = os.path.dirname(__file__)

REQUIRED_KEYS = [
    "interface_details", "ip_int_brief", "cdp_neighbors", "cdp_neighbors_detail",
    "serial_string"
]

test_file_path = os.path.join(current_dir, 'mock_data_cisco.json')

with open(test_file_path, "r") as f:
    test_data = json.load(f)

# Ensure all required keys are present and populated
for key in REQUIRED_KEYS:
    if key not in test_data or not test_data[key]:
        raise ValueError(f"Missing or empty key in test data: {key}")

mock_interface_details = [MyDict(x) for x in test_data["interface_details"]]
mock_ip_int_brief = [MyDict(x) for x in test_data["ip_int_brief"]]
mock_cdp_neighbors = [MyDict(x) for x in test_data["cdp_neighbors"]]
mock_cdp_neighbors_detail = [MyDict(x) for x in test_data["cdp_neighbors_detail"]]
mock_serial = test_data["serial_string"]


class TestCiscoSSHDevice(unittest.TestCase):
    @patch('network_automation.cisco.ConnectHandler')  # Mock the ConnectHandler class
    def test_get_interface_details(self, mock_connect_handler):
        # Set up the mock connection's behavior
        mock_connection = MagicMock()
        mock_connection.send_command.return_value = mock_interface_details
        mock_connect_handler.return_value = mock_connection

        # Create an instance of CiscoSSHDevice
        device = CiscoSSHDevice(hostname='192.168.1.1', username='user', password='pass')

        # Call the method under test
        result = device.get_interface_details()

        # Assert the result is as expected
        self.assertEqual(len(result), 3)
        for idx, interface in enumerate(mock_interface_details):
            # self.assertEqual(result[idx].interface, interface['interface'])
            if idx == 1:
                self.assertEqual(result[idx].interface, 'Vlan35')
                self.assertEqual(result[idx].link_status, 'up')
                self.assertEqual(result[idx].protocol_status, 'up , Autostate Enabled')
                self.assertEqual(result[idx].description, 'router1_transit')

        # Ensure send_command was called with the correct command
        mock_connection.send_command.assert_called_once_with('show interface', use_textfsm=True, read_timeout=30)

    @patch('network_automation.cisco.ConnectHandler')  # Mock the ConnectHandler class
    def test_get_ip_interface_brief(self, mock_connect_handler):
        # Set up the mock connection's behavior
        mock_connection = MagicMock()
        mock_connection.send_command.return_value = mock_ip_int_brief
        mock_connect_handler.return_value = mock_connection

        # Create an instance of CiscoSSHDevice
        device = CiscoSSHDevice(hostname='192.168.1.1', username='user', password='pass')

        # Call the method under test
        result = device.get_interface_details()

        # Assert the result is as expected
        self.assertEqual(len(result), 4)
        for idx, interface in enumerate(mock_ip_int_brief):
            # self.assertEqual(result[idx].interface, interface['interface'])
            if idx == 0:
                self.assertEqual(result[idx].interface, 'GigabitEthernet1')
                self.assertEqual(result[idx].ip_address, '192.168.30.50')
                self.assertEqual(result[idx].proto, 'up')

        # Ensure send_command was called with the correct command
        mock_connection.send_command.assert_called_once_with('show interface', use_textfsm=True, read_timeout=30)

    @patch('network_automation.cisco.ConnectHandler')  # Mock the ConnectHandler class
    def test_get_device_serial(self, mock_connect_handler):
        # Set up the mock connection's behavior
        mock_connection = MagicMock()
        mock_connection.send_command.return_value = mock_serial
        mock_connect_handler.return_value = mock_connection

        # Create an instance of CiscoSSHDevice
        device = CiscoSSHDevice(hostname='192.168.1.1', username='user', password='pass')

        # Call the method under test
        serial_number = device.get_device_serial()

        # Assert the result is as expected
        self.assertEqual(serial_number, "FOX3986YDP3")

        # Ensure send_command was called with the correct command
        mock_connection.send_command.assert_called_once_with('show version | include Processor')


class TestCDPNeighbors(unittest.TestCase):
    @patch('network_automation.cisco.ConnectHandler')
    def test_get_cdp_neighbors_summary(self, mock_connect_handler):
        # Set up the mock connection
        mock_connection = MagicMock()
        mock_connection.send_command.return_value = mock_cdp_neighbors
        mock_connect_handler.return_value = mock_connection

        device = CiscoSSHDevice(hostname='192.168.1.1', username='user', password='pass')
        result = device.get_cdp_neighbors(detail=False)

        # Assert result matches expected mock data
        self.assertEqual(len(result), 3)
        for idx, neighbor in enumerate(mock_cdp_neighbors):
            if idx == 2:
                self.assertEqual(result[idx].local_interface, 'Hun 2/0/9')
                self.assertEqual(result[idx].platform, 'C9410R')

        # Ensure the correct command was executed
        mock_connection.send_command.assert_called_once_with(
            'show cdp neighbors', use_textfsm=True, read_timeout=10
        )

    @patch('network_automation.cisco.ConnectHandler')
    def test_get_cdp_neighbors_detail(self, mock_connect_handler):
        mock_connection = MagicMock()
        mock_connection.send_command.return_value = mock_cdp_neighbors_detail
        mock_connect_handler.return_value = mock_connection

        device = CiscoSSHDevice(hostname='192.168.1.1', username='user', password='pass')
        result = device.get_cdp_neighbors(detail=True)

        self.assertEqual(len(result), 4)
        for idx, neighbor in enumerate(mock_cdp_neighbors_detail):
            if idx == 4:
                self.assertEqual(result[idx].neighbor_interface, "FortyGigabitEthernet5/0/9")

        mock_connection.send_command.assert_called_once_with(
            'show cdp neighbors detail', use_textfsm=True, read_timeout=10
        )
