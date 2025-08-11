from ipaddress import IPv4Network
from ipaddress import IPv4Address
from ipaddress import ip_network
from requests.auth import HTTPBasicAuth
import requests
import json
import urllib3

urllib3.disable_warnings()


def is_ip(ip):
    try:
        IPv4Address(ip)
        return True
    except:
        return False


def is_subnet(subnet):
    try:
        IPv4Network(subnet)
        return True
    except:
        return False


def get_available_ips(subnet, used_ips, count):
    network = IPv4Network(subnet)
    unused_ips = []
    for ip in network.hosts():
        ip_str = str(ip)
        if ip_str not in used_ips and ip_str != str(network.network_address):
            unused_ips.append(ip_str)
            if len(unused_ips) == count:
                break
    return unused_ips


def check_subnet_overlap(subnet, subnets):
    net = IPv4Network(subnet)
    overlapped = []
    for s in subnets:
        other = IPv4Network(s)
        if net.overlaps(other):
            overlapped.append(other)
    return overlapped


def is_vlan(vlan):
    try:
        if 0 <= int(vlan) <= 4096:
            return True
        else:
            return False
    except:
        return False


def check_create_multiple_subnet(item):
    status = True
    region = item[0]
    location = item[1]
    group = item[2]
    group_subnet = item[3]
    subnet = item[4]
    vlan = item[5]
    name = item[6]
    if region == "":
        status = False
    elif location == "":
        status = False
    elif group == "":
        status = False
    elif is_subnet(group_subnet) is False:
        status = False
    elif is_subnet(subnet) is False:
        status = False
    elif is_vlan(vlan) is False:
        status = False
    elif name == "":
        status = False
    elif ip_network(subnet).subnet_of(ip_network(group_subnet)) is False:
        status = False
    else:
        return status


def get_jenkins_crumb(url, jk_user, jk_passwd):
    try:
        res = requests.get(
            url=url, auth=HTTPBasicAuth(jk_user, jk_passwd), verify=False
        )
        if res.ok:
            jk_crumb = json.loads(res.text)["crumb"]
            return {"status": "success", "jk_crumb": jk_crumb}
        else:
            error = res.text
            return {"status": "failed", "error": error}
    except Exception as error:
        if "ConnectionError" in str(error):
            error = "Network error, ICMS can not connect to Jenkins"
        return {"status": "failed", "error": error}


def run_jenkins_job(url, jk_user, jk_passwd, jk_crumb):
    try:
        headers = {"Jenkins-Crumb": jk_crumb}
        res = requests.post(
            url=url,
            auth=HTTPBasicAuth(jk_user, jk_passwd),
            headers=headers,
            verify=False,
        )
        if res.ok:
            return {"status": "success"}
        else:
            error = res.text
            return {"status": "failed", "error": error}
    except Exception as error:
        if "ConnectionError" in str(error):
            error = "Network error, ICMS can not connect to Jenkins"
        return {"status": "failed", "error": error}
