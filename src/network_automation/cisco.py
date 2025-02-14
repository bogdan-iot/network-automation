import logging
from network_automation import environment
from mydict import MyDict
from netmiko import ConnectHandler


class CiscoSSHDevice(object):
    """
    This class defines methods for fetching data from a Cisco device using NetMiko
    """
    def __init__(self, hostname, username=None, password=None):
        if not hostname:
            raise ValueError("Hostname is mandatory")

        self.hostname = hostname
        # Username and passwords can be provided as parameters (preferred) or as environment variables
        self.username = username or environment.get_cisco_username()
        self.password = password or environment.get_cisco_password()

        netmiko_device = {
            'device_type': "cisco_ios",
            'ip': self.hostname,
            'username': self.username,
            'password': self.password,
            'secret': self.password
        }
        self.conn = ConnectHandler(**netmiko_device)

    def execute_show_command(self, command, parse=True, timeout=10):
        """
        This method executes a command on Cisco CLI and returns the result
        :param command: The command to run
        :param parse: Parse the output with textfsm (True)
        :param timeout: Set the timeout for executing the command and getting the result
        :return:
        """
        logging.info(f"Executing command '{command}' on {self.hostname}")
        if parse:
            return self.conn.send_command(command, use_textfsm=True, read_timeout=timeout)

        return self.conn.send_command(command)

    def get_interface_details(self, timeout=30):
        """
        This method executes the 'show interface' command and returns the result parsed with textfsm
        :param timeout: Set the timeout for executing the command and getting the result
        :return:
        """
        interfaces = self.execute_show_command('show interface', timeout=timeout)
        return [MyDict(x) for x in interfaces]

    def get_device_serial(self):
        """
        This method gets the serial number of a device
        :return:
        """
        serial = self.conn.send_command('show version | include Processor')
        return serial.split(' ')[-1]

    def get_cdp_neighbors(self, parse=True, detail=False):
        """
        This method retrieves the CDP neighbors of the device
        :return:
        """
        if detail:
            command = 'show cdp neighbors detail'
        else:
            command = 'show cdp neighbors'
        if parse:
            return self.conn.send_command(command, use_textfsm=True)

        return self.conn.send_command(command)
