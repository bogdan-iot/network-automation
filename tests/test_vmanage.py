import json
import os
import pytest
from mydict import MyDict
from unittest.mock import patch, MagicMock
from network_automation.vmanage import VManage

current_dir = os.path.dirname(__file__)

test_file_path = os.path.join(current_dir, 'mock_data_vmanage.json')


class TestVManage:
    @pytest.fixture(autouse=True)
    def setup(self):
        with (patch("network_automation.vmanage.Authentication") as mock_auth,
              patch("network_automation.vmanage.requests.get") as mock_get):
            # Load mock data from file
            with open(test_file_path, "r") as file:
                mock_data = json.load(file)

            # Mock authentication attributes
            self.mock_auth_instance = mock_auth.return_value
            self.mock_auth_instance.jsessionid = "JSESSIONID=mock_session"
            self.mock_auth_instance.token = "mock_token"
            self.mock_auth_instance.host = "mock_host"
            self.mock_auth_instance.port = 443
            self.mock_auth_instance.proxies = {}

            # Mock response from the API
            self.mock_response = MagicMock()
            self.mock_response.status_code = 200
            self.mock_response.json.return_value = mock_data
            mock_get.return_value = self.mock_response

            # Instantiate VManage with the mocked authentication
            self.vmanage = VManage()

            # Mock _get_entity method since it's used in get_device_list
            self.vmanage._get_entity = MagicMock()
            self.vmanage._get_entity.return_value.data = mock_data

    def test_get_device_serial(self):
        # Call the method under test
        result = self.vmanage.get_device_list()

        # Assertions
        assert result['devices'][0]['board-serial'] == 'A1B2C3D4'
        self.vmanage._get_entity.assert_called_once_with("\\device")

    def test_get_wan_interface(self):
        # Call the method under test
        result = self.vmanage.get_wan_interface_list('1.1.1.1')

        # Assertions
        assert result['interfaces'][0]['board-serial'] == 'A1B2C3D4'
        self.vmanage._get_entity.assert_called_once_with("\\interface")
