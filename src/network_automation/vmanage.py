import os
import requests
from mydict import MyDict

class Authentication:
    def __init__(self, host=None, port=None, usr=None, pwd=None, proxies=None):
        self.host = host or os.environ.get("VMANAGE_HOST")
        self.port = port or os.environ.get("VMANAGE_PORT", 443)
        self.usr = usr or os.environ.get("VMANAGE_USER")
        self.pwd = pwd or os.environ.get("VMANAGE_PASS")
        if proxies is None:
            self.proxies = {}

        self.jsessionid = self.get_jsessionid()
        self.token = self.get_token()

    def get_jsessionid(self):
        api = "/j_security_check"
        base_url = f'https://{self.host}:{self.port}'
        url = base_url + api
        payload = {'j_username': self.usr, 'j_password': self.pwd}

        response = requests.post(url=url, data=payload, proxies=self.proxies, verify=False)
        try:
            cookies = response.headers["Set-Cookie"]
            jsessionid = cookies.split(";")
        except:
            raise ConnectionError("No valid JSESSION ID returned")

        return jsessionid[0]

    def get_token(self):
        headers = {'Cookie': self.jsessionid}
        base_url = f'https://{self.host}:{self.port}'
        api = "/dataservice/client/token"
        url = base_url + api
        response = requests.get(url=url, headers=headers, proxies=self.proxies, verify=False)
        if response.status_code != 200:
            raise ConnectionError("No valid token returned")

        return response.text


class VManage:
    def __init__(self):
        self.auth = Authentication()
        # self.jsessionid = self.auth.get_jsessionid(vmanage_host, vmanage_port, vmanage_username, vmanage_password)
        # self.token = self.auth.get_token(vmanage_host, vmanage_port, self.jsessionid)
        self.base_url = f'https://{self.auth.host}:{self.auth.port}/dataservice'
        self.proxies = self.auth.proxies

        if self.auth.token is not None:
            self.headers = {'Content-Type': "application/json", 'Cookie': self.auth.jsessionid,
                            'X-XSRF-TOKEN': self.auth.token}
        else:
            self.headers = {'Content-Type': "application/json", 'Cookie': self.auth.jsessionid}

    def get_prefix_lists(self):
        url_path = '/template/policy/list/dataprefix'

        return MyDict(requests.get(self.base_url + url_path, headers=self.headers,
                                   proxies=self.proxies, verify=False).json())

    def get_security_policy(self):
        url_path = '/template/policy/security'

        return MyDict(requests.get(self.base_url + url_path, headers=self.headers,
                                   proxies=self.proxies, verify=False).json())

    def get_firewall_policy(self, policy_id):
        url_path = f'/template/policy/definition/zonebasedfw/{policy_id}'

        return MyDict(requests.get(self.base_url + url_path, headers=self.headers,
                                   proxies=self.proxies, verify=False).json())