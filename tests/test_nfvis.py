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
    def mock_get_platform_details(self):
        """Mock the get_platform_details method"""
        return mock_data

    @patch.object(NFVISServer, 'get_platform_details')
    def test_server_serial(self, mock_method, mock_get_platform_details):
        """Test for checking the retrieved serial number of a server"""

        mock_method.return_value = mock_get_platform_details  # Mock return value
        # Create an instance of NFVIS
        instance = NFVISServer(hostname="fake-hostname", username="fake-user", password="fake-password")

        # Inject the mock nfvis object into the instance
        instance.platform = mock_get_platform_details['platform_info:platform-detail']
        # instance.platform = mock_nfvis.get_platform_details()["platform_info:platform-detail"]

        mock_method.assert_called_once()  # Ensure the mock was called

        # Call the method under test
        serial = instance.get_serial()

        # Assertions
        assert serial == "FGL3913OTVX"

