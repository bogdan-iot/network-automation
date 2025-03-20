import json
import requests
from network_automation import environment

header = {
    "content-type": "application/vnd.yang.collection+json",
    "Accept": "application/vnd.yang.data+json",
}


class NFVISServer(object):
    """
    This represents a Cisco NFVIS server
    """
    def __init__(self, hostname, username=None, password=None, verify=True):
        if not hostname:
            raise ValueError("Hostname is missing")

        self.url = 'https://' + hostname
        self.username = username or environment.get_cisco_username()
        self.password = password or environment.get_cisco_password()

        if not username or not password:
            raise ValueError("username/password is missing and could not be retrieved from environment variables")

        self.session = requests.Session()
        if not verify:
            self.session.verify = False

        self.session.auth = (username, password)
        self.platform = None

    def get_platform_details(self):
        if self.platform:
            return self.platform

        uri = self.url + '/api/operational/platform-detail'
        resp = self.session.get(uri, headers=header)

        self.platform = json.loads(resp.text)["platform_info:platform-detail"]

    def get_serial(self):
        self.get_platform_details()
        return self.platform["hardware_info"]["SN"]

    def get_pid(self):
        self.get_platform_details()
        return self.platform["hardware_info"]["PID"]

    def get_version(self):
        self.get_platform_details()
        return self.platform["hardware_info"]["Version"]
