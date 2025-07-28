from network_automation.utils import ip_reachable
from unittest.mock import patch


@patch("subprocess.call")
def test_ip_reachable_success(mock_subprocess_call):
    # Mock the return value of subprocess.call to simulate a successful ping
    mock_subprocess_call.return_value = 0

    # Call the function under test
    result = ip_reachable("example.com")

    # Assert that the function returns True for a successful ping
    assert result is True

    # Assert that subprocess.call was called with the expected arguments
    mock_subprocess_call.assert_called()


@patch("subprocess.call")
def test_ip_reachable_failure(mock_subprocess_call):
    # Mock the return value of subprocess.call to simulate a failed ping
    mock_subprocess_call.return_value = 1

    # Call the function under test
    result = ip_reachable("example.com")

    # Assert that the function returns False for a failed ping
    assert result is False

    # Assert that subprocess.call was called with the expected arguments
    mock_subprocess_call.assert_called()
