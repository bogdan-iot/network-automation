import json
import os
import pytest
from mydict import MyDict
from network_automation.nfvis import NFVISServer
from unittest.mock import patch

current_dir = os.path.dirname(__file__)

test_file_path = os.path.join(current_dir, 'mock_data_nfvis.json')

with open(test_file_path, "r") as f:
    netbox_data = json.load(f)
    mock_data = MyDict(netbox_data)


class TestNFVIS:
    @pytest.fixture
    def get_mock_data(self):
        """Mock the get_platform_details method"""
        return mock_data

    @patch.object(NFVISServer, 'get_platform_details')
    def test_server_serial(self, mock_method, get_mock_data):
        """Test for checking the retrieved serial number of a server"""

        mock_method.return_value = get_mock_data  # Mock return value
        # Create an instance of NFVIS
        instance = NFVISServer(hostname="fake-hostname", username="fake-user", password="fake-password")

        # Inject the mock nfvis object into the instance
        instance.platform = get_mock_data['platform_info:platform-detail']

        mock_method.assert_called_once()  # Ensure the mock was called

        # Call the method under test
        serial = instance.get_serial()

        # Assertions
        assert serial == "FGL3913OTVX"

    # @patch.object(NFVISServer, 'get_interfaces')
    # def test_interface_mac(self, mock_method, get_mock_data):
    #     """Test for checking the retrieved MAC address of an interface number of a server"""
    #
    #     mock_method.return_value = get_mock_data  # Mock return value
    #     # Create an instance of NFVIS
    #     instance = NFVISServer(hostname="fake-hostname", username="fake-user", password="fake-password")
    #
    #     # Inject the mock nfvis object into the instance
    #     interfaces = get_mock_data['pnic:pnics']['pnic']
    #
    #     # mock_method.assert_called_once()  # Ensure the mock was called
    #
    #     # Call the method under test
    #     mac = instance.get_interfaces()
    #
    #     # Assertions
    #     assert mac == "FGL3913OTVX"


    @patch.object(NFVISServer, 'get_platform_details') # Mock get platform details
    @patch.object(NFVISServer, 'get_interfaces')  # Mock the method before it's called
    def test_get_interfaces(self, mock_get_interfaces, mock_get_platform_details, get_mock_data):
        mock_get_platform_details.return_value = None  # Prevents the actual API call
        """Test for checking the retrieved network interfaces"""
        mock_get_interfaces.return_value = get_mock_data['pnic:pnics']['pnic']  # Mock return value

        # Create an instance of NFVIS (mock prevents real requests)
        instance = NFVISServer(hostname="fake-hostname", username="fake-user", password="fake-password")

        # Manually inject platform data to avoid real API calls
        instance.platform = get_mock_data["platform_info:platform-detail"]

        # Call method under test
        interfaces = instance.get_interfaces()

        # Ensure get_interfaces was called once
        mock_get_interfaces.assert_called_once()
        mock_get_platform_details.assert_called_once()

        # Assertions
        assert isinstance(interfaces, list)  # Ensure the result is a list
        assert len(interfaces) == 2  # Ensure correct number of interfaces
        assert interfaces[0]["name"] == "eth0-1"
        assert interfaces[1]["name"] == "eth0-2"
        assert interfaces[1]["mac_address"] == "cc:88:7a:59:f1:eb"

    @patch.object(NFVISServer, 'get_platform_details') # Mock get platform details
    @patch.object(NFVISServer, 'get_switch_interfaces')  # Mock the method before it's called
    def test_get_switch_interfaces(self, mock_get_switch_interfaces, mock_get_platform_details, get_mock_data):
        mock_get_platform_details.return_value = None  # Prevents the actual API call
        """Test for checking the retrieved switch interfaces"""
        mock_get_switch_interfaces.return_value = get_mock_data['switch:status']['gigabitEthernet']  # Mock return value

        # Create an instance of NFVIS (mock prevents real requests)
        instance = NFVISServer(hostname="fake-hostname", username="fake-user", password="fake-password")

        # Manually inject platform data to avoid real API calls
        instance.platform = get_mock_data["platform_info:platform-detail"]

        # Call method under test
        switchports = instance.get_switch_interfaces()

        # Ensure get_interfaces was called once
        mock_get_switch_interfaces.assert_called_once()
        mock_get_platform_details.assert_called_once()

        # Assertions
        assert isinstance(switchports, list)  # Ensure the result is a list
        assert len(switchports) == 3  # Ensure correct number of interfaces
        assert switchports[0]["Port"] == "1/0"
        assert switchports[1]["Port"] == "1/1"
        assert switchports[1]["macaddr"] == "a7:8b:0c:0d:7f:4a"

    @patch.object(NFVISServer, 'get_platform_details') # Mock get platform details
    @patch.object(NFVISServer, 'get_switchport_status')  # Mock the method before it's called
    def test_get_switchport_status(self, mock_get_switchport_status, mock_get_platform_details, get_mock_data):
        mock_get_platform_details.return_value = None  # Prevents the actual API call
        """Test for checking the retrieved switchport status"""
        mock_get_switchport_status.return_value = get_mock_data['switch:switchPort']['port-channel']  # Mock return value

        # Create an instance of NFVIS (mock prevents real requests)
        instance = NFVISServer(hostname="fake-hostname", username="fake-user", password="fake-password")

        # Manually inject platform data to avoid real API calls
        instance.platform = get_mock_data["platform_info:platform-detail"]

        # Call method under test
        switchports = instance.get_switchport_status()

        # Ensure get_interfaces was called once
        mock_get_switchport_status.assert_called_once()
        mock_get_platform_details.assert_called_once()

        # Assertions
        assert isinstance(switchports, list)  # Ensure the result is a list
        assert len(switchports) == 2  # Ensure correct number of interfaces
        assert switchports[0]["switchport-mode"] == "enable"
        assert switchports[1]["adminstrative-mode"] == "access"
