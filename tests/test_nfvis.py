import json
import os
import pytest
from mydict import MyDict
from network_automation.nfvis import NFVISServer
from unittest.mock import MagicMock

current_dir = os.path.dirname(__file__)

test_file_path = os.path.join(current_dir, 'mock_data_nfvis.json')

with open(test_file_path, "r") as f:
    netbox_data = json.load(f)
    mock_data = MyDict(netbox_data)


class TestNFVIS:
    @pytest.fixture
    def mock_nfvis(self):
        # Create a mock dcim object and mock the devices.all() method
        mock_nfvis = MagicMock()
        mock_nfvis.get_platform_details.return_value = mock_data
        return mock_nfvis

    def test_server_serial(self, mock_nfvis):
        """Test for checking the retrieved serial number of a server"""

        # Create an instance of NFVIS
        instance = NFVISServer(hostname="fake-hostname", username="fake-user", password="fake-password")

        # Inject the mock nfvis object into the instance
        instance.platform = mock_nfvis.get_platform_details()["platform_info:platform-detail"]

        # Call the method under test
        serial = instance.get_serial()

        # Assertions
        assert serial == "FGL3913OTVX"
        mock_nfvis.get_platform_details.assert_called_once()  # Ensure the mock was called
