import os
import re
import requests
from network_automation import environment


class CiscoACI:
    def __init__(self, url, username=None, password=None):
        apic_auth_data = {
            "aaaUser": {
                "attributes": {
                    "name": username or environment.get_cisco_username(),
                    "pwd": password or environment.get_cisco_password()
                }
            }
        }

        self.url = url
        self.auth_url = self.url + "aaaLogin.json"

        self.session = requests.session()
        self.session.verify = False
        self.session.post(self.auth_url, json=apic_auth_data, verify=False)

    def get_aci_pods(self):
        fabric_class = "node/class/fabricPod.json"
        fabric_url = self.url + fabric_class

        aci_fabrics = self.session.get(fabric_url)
        return [x['fabricPod']['attributes']['dn'] for x in aci_fabrics.json()['imdata']]

    def get_aci_nodes(self, pod):
        node_class = f"node/mo/{pod}.json?query-target=children&target-subtree-class=fabricNode"
        node_url = self.url + node_class

        return [x['fabricNode']['attributes'] for x in self.session.get(node_url).json()['imdata']]

    def get_node_mgmt_ip(self, path):
        mgmt_intf_class = f"node/mo/{path}/sys/ipv4/inst/dom-management/if-[mgmt0].json?query-target=children&target-subtree-class=ipv4Addr"
        mgmt_intf_url = self.url + mgmt_intf_class

        result = self.session.get(mgmt_intf_url).json()

        try:
            mgmt_ip = result['imdata'][0]['ipv4Addr']['attributes']['addr']
        except IndexError:
            print(f"Could not get management IP address: {result}")
            return None

        return mgmt_ip

    def get_physical_intfs(self, path):
        physical_intfs_class = f"node/class/{path}/l1PhysIf.json?rsp-subtree=children&rsp-subtree-class=ethpmPhysIf"
        physical_intfs_url = self.url + physical_intfs_class
        physical_intfs = self.session.get(physical_intfs_url).json()

        result = [{
            'name': x['l1PhysIf']['attributes']['id'],
            'admin_status': x['l1PhysIf']['attributes']['adminSt'],
            'desc': x['l1PhysIf']['attributes']['descr'],
            'mode': x['l1PhysIf']['attributes']['mode'],
            'mac': x['l1PhysIf']['children'][0]['ethpmPhysIf']['attributes']['backplaneMac']
        } for x in physical_intfs['imdata']]

        return result

    def get_l3_loopbacks(self, path):
        loopback_intfs_class = f"node/class/{path}/l3LbRtdIf.json?query-target=children&target-subtree-class=ethpmLbRtdIf"
        loopback_intfs_url = self.url + loopback_intfs_class
        loopback_intfs = self.session.get(loopback_intfs_url).json()['imdata']

        for intf in loopback_intfs:
            intf_id_match = re.search(r'\[(.*?)\]', intf['ethpmLbRtdIf']['attributes']['dn'])
            if intf_id_match:
                intf['id'] = intf_id_match.group(1)
                loopback_ip_class = f"node/mo/{path}/sys/ipv4/inst/dom-overlay-1/if-[{intf['id']}].json?query-target=children&target-subtree-class=ipv4Addr"
                loopback_ip_url = self.url + loopback_ip_class
                try:
                    intf['ipv4_addr'] = self.session.get(loopback_ip_url).json()['imdata'][0]['ipv4Addr']['attributes']['addr']
                except KeyError:
                    print(f"Could not get IP address for interface {intf['id']}")

        return loopback_intfs

    def get_tenants(self):
        tenants = self._get_class("node/class/fvTenant.json")

        return [x['fvTenant']['attributes']['name'] for x in tenants]

    def get_tenant_bridge_domains(self, tenant_name):
        bds = self._get_class(f"node/mo/uni/{tenant_name}.json?query-target=children&target-subtree-class=fvBD")

        return [x['fvBD']['attributes']['name'] for x in bds]

    def _get_class(self, url_path):
        class_url = self.url + url_path

        return self.session.get(class_url).json()['imdata']
