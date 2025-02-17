import os
import requests
from mydict import MyDict


class Authentication:
    def __init__(self, host, port, usr, pwd, proxies):
        self.host = host or os.environ.get("VMANAGE_HOST")
        self.port = port or os.environ.get("VMANAGE_PORT", 443)
        self.usr = usr or os.environ.get("VMANAGE_USER")
        self.pwd = pwd or os.environ.get("VMANAGE_PASS")
        self.proxies = proxies or {}

        self.jsessionid = self.get_jsessionid()
        self.token = self.get_token()

    def get_jsessionid(self):
        api = "/j_security_check"
        base_url = f'https://{self.host}:{self.port}'
        url = base_url + api
        payload = {'j_username': self.usr, 'j_password': self.pwd}

        try:
            response = requests.post(url=url, data=payload, proxies=self.proxies, verify=False)
        except requests.exceptions.ProxyError:
            raise ConnectionError("Please check vManage URL and proxy settings")
        if response.text:
            raise ConnectionError("Authentication issue")

        cookies = response.headers["Set-Cookie"]
        jsessionid = cookies.split(";")

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
    def __init__(self, host=None, port=None, usr=None, pwd=None, proxies=None):
        self.auth = Authentication(host, port, usr, pwd, proxies)
        self.base_url = f'https://{self.auth.host}:{self.auth.port}/dataservice'
        self.proxies = self.auth.proxies

        if self.auth.token is not None:
            self.headers = {'Content-Type': "application/json", 'Cookie': self.auth.jsessionid,
                            'X-XSRF-TOKEN': self.auth.token}
        else:
            self.headers = {'Content-Type': "application/json", 'Cookie': self.auth.jsessionid}

    def get_device_list(self):
        url_path = '\device'
        return self._get_entity(url_path).data

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

    def get_wan_interface_list(self, ip_address=None):
        if not ip_address:
            raise ValueError("Missing parameter: ip_address")
        url_path = f'/device/control/waninterfaces?deviceId={ip_address}'

        return self._get_entity(url_path).data

    def _get_entity(self, url_path):
        return MyDict(requests.get(self.base_url + url_path, headers=self.headers,
                                   proxies=self.proxies, verify=False).json())

    def get_tunnel_metrics(self, device_ip, remote_endpoints, hours=24, interval=1):
        url_path = '/statistics/approute/fec/aggregation'
        query = {
            "query": {
                "condition": "AND",
                "rules":
                    [
                        {
                            "value": [str(hours)],
                            "field": "entry_time",
                            "type": "date",
                            "operator": "last_n_hours"
                        },
                        {
                            "value": [device_ip],
                            "field": "vdevice_name",
                            "type": "string",
                            "operator": "in"
                        }
                    ]
            },
            "aggregation":
                {
                    "field": [
                        {
                            "property": "name",
                            "sequence": 1,
                            "size": 262},
                        {
                            "property": "state",
                            "sequence": 1
                        },
                        {
                            "property": "proto",
                            "sequence": 2
                        }
                    ],
                    "histogram": {
                        "property": "entry_time",
                        "type": "hour",
                        "interval": interval,
                        "order": "asc"
                    },
                    "metrics": [
                        {
                            "property": "loss_percentage",
                            "type": "avg"},
                        {
                            "property": "vqoe_score",
                            "type": "avg"
                        },
                        {
                            "property": "latency",
                            "type": "avg"
                        },
                        {
                            "property": "jitter",
                            "type": "avg"
                        },
                        {
                            "property": "rx_octets",
                            "type": "sum"
                        },
                        {
                            "property": "tx_octets",
                            "type": "sum"}
                    ]
                }
        }

        result = MyDict(requests.post(self.base_url + url_path, headers=self.headers,
                                      proxies=proxies, data=json.dumps(query), verify=False).json())

        filtered_list = []

        for endpoint in remote_endpoints:
            filtered_list.extend([x for x in result.data if endpoint in x.name])

        return filtered_list
