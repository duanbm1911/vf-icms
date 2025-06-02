from ipaddress import IPv4Address
import re


def is_ipaddress(ip):
    try:
        IPv4Address(ip)
        return True
    except:
        return False


def is_domain(domain):
    regex = r"^(?!:\/\/)([a-zA-Z0-9-_]+(\.[a-zA-Z0-9-_]+)*\.[a-zA-Z]{2,63}|localhost)$"
    if re.match(regex, domain):
        return True
    else:
        return False


def is_number(number):
    try:
        int(number)
        if int(number) < 0 or int(number) > 65536:
            return False
        return True
    except:
        return False


def check_pool_member(datalist):
    for item in datalist:
        if item.split(":") != [""] and len(item.split(":")) > 1:
            member_ip = item.split(":")[0]
            member_port = item.split(":")[1]
            if not is_ipaddress(member_ip):
                return False
            elif not is_number(member_port):
                return False
        else:
            return False
    return True


def check_virtual_server(data):
    if data.split(":") != [""] and len(data.split(":")) > 1:
        vs_ip = data.split(":")[0]
        vs_port = data.split(":")[1]
        if not is_ipaddress(vs_ip):
            return False
        elif not is_number(vs_port):
            return False
        return True
    else:
        return False


def check_create_vs_input(data, index):
    rule_index = index + 1
    error_message = str()
    if data:
        f5_device_ip = data[0]
        service_name = data[1]
        virtual_server = data[2]
        pool_member = data[3].split("\n")
        pool_monitor = data[4]
        pool_lb_method = data[5]
        f5_template_name = data[10]
        if f5_device_ip == "":
            error_message = f"Rule index {rule_index}: F5 device is not valid"
        elif service_name == "":
            error_message = f"Rule index {rule_index}: Service name is not valid"
        elif not check_virtual_server(virtual_server):
            error_message = f"Rule index {rule_index}: Virtual server is not valid"
        elif not check_pool_member(pool_member):
            error_message = f"Rule index {rule_index}: Pool member is not valid"
        elif pool_monitor == "":
            error_message = (
                f"Rule index {rule_index}: Pool monitor profile is not valid"
            )
        elif pool_lb_method == "":
            error_message = f"Rule index {rule_index}: Pool LB method is not valid"
        elif f5_template_name == "":
            error_message = f"Rule index {rule_index}: F5 template name is not valid"
    return error_message
