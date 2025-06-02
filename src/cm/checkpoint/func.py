from ipaddress import IPv4Address
from ipaddress import ip_network, ip_address
from cm.models import *
import re, json


def is_subnet(subnet):
    try:
        ip_network(subnet)
        return True
    except:
        return False


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


def is_user(user):
    obj = user.split("/")
    if len(obj) == 2 and "user" == obj[0] or "partner" == obj[0]:
        return True
    return False

def is_ip_range(value):
    ip_range_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    if not re.match(ip_range_pattern, value):
        return False
    
    start_ip, end_ip = value.split('-')
    return True

def ip_in_network(ip, network):
    try:
        ip_obj = ip_address(ip)
        net_obj = ip_network(network, strict=False)
        return ip_obj in net_obj
    except ValueError:
        return False
    
def network_in_network(net1, net2):
    try:
        n1 = ip_network(net1, strict=False)
        n2 = ip_network(net2, strict=False)
        return n1.subnet_of(n2)
    except ValueError:
        return False
    
def ip_in_range(ip, ip_range):
    try:
        ip_obj = ip_address(ip)
        start_ip, end_ip = ip_range.split('-')
        start_obj = ip_address(start_ip)
        end_obj = ip_address(end_ip)
        
        return start_obj <= ip_obj <= end_obj
    except ValueError:
        return False

def range_in_range(range1, range2):
    try:
        start1, end1 = range1.split('-')
        start2, end2 = range2.split('-')
        
        start1_obj = ip_address(start1)
        end1_obj = ip_address(end1)
        start2_obj = ip_address(start2)
        end2_obj = ip_address(end2)
        
        return start2_obj <= start1_obj and end1_obj <= end2_obj
    except ValueError:
        return False

def range_in_network(ip_range, network):
    try:
        net_obj = ip_network(network, strict=False)
        start_ip, end_ip = ip_range.split('-')
        start_obj = ip_address(start_ip)
        end_obj = ip_address(end_ip)
        
        return start_obj in net_obj and end_obj in net_obj
    except ValueError:
        return False

def check_list_object(datalist):
    for item in datalist:
        if item != "any" and is_ipaddress(item) is True:
            pass
        elif item != "any" and is_subnet(item) is True:
            pass
        elif item != "any" and is_ip_range(item) is True:
            pass
        elif item != "any" and is_domain(item) is True:
            pass
        elif item != "any" and is_user(item) is True:
            pass
        elif item == "any" and len(datalist) == 1:
            pass
        else:
            return False
    return True


def check_list_protocol(datalist):
    try:
        for item in datalist:
            list_item = item.split("-")
            if len(list_item) == 1:
                if list_item[0] != "any":
                    return False
            elif len(list_item) == 2:
                if list_item[0] not in ["tcp", "udp"]:
                    return False
                else:
                    int(list_item[1])
                    if int(list_item[1]) < 0 or int(list_item[1]) > 65536:
                        return False
            elif len(list_item) == 3:
                if list_item[0] not in ["tcp", "udp"]:
                    return False
                else:
                    int(list_item[1])
                    int(list_item[2])
                    if int(list_item[1]) > int(list_item[2]):
                        return False
                    elif int(list_item[1]) < 0 or int(list_item[1]) > 65536:
                        return False
                    elif int(list_item[2]) < 0 or int(list_item[2]) > 65536:
                        return False
            else:
                return False
        return True
    except:
        return False



def check_cp_access_rule_input(data, index):
    rule_index = index + 1
    error_message = str()
    if data != []:
        policy = data[0]
        rule_name = data[2]
        source = [i.replace(" ", "").replace("\r", "") for i in data[3].split("\n") if i.strip()]
        destination = [i.replace(" ", "").replace("\r", "") for i in data[4].split("\n") if i.strip()]
        protocol = [i.replace(" ", "").replace("\r", "") for i in data[5].split("\n") if i.strip()]
        section = data[7]
        
        if policy == "":
            error_message = f"Rule index {rule_index}: Policy template name can not be empty"
        elif rule_name == "":
            error_message = f"Rule index {rule_index}: Policy template rule_name can not be empty"
        elif not source:
            error_message = f"Rule index {rule_index}: Source address is invalid"
        elif "any" in source and len(source) > 1:
            error_message = f"Rule index {rule_index}: Source address is invalid"
        elif not check_list_object(source):
            error_message = f"Rule index {rule_index}: Source address is invalid"
        elif not destination:
            error_message = f"Rule index {rule_index}: Destination address is invalid"
        elif "any" in destination and len(destination) > 1:
            error_message = f"Rule index {rule_index}: Destination address is invalid"
        elif not check_list_object(destination):
            error_message = f"Rule index {rule_index}: Destination address is invalid"
        elif not check_list_protocol(protocol):
            error_message = f"Rule index {rule_index}: Protocol is invalid"
        elif section == "":
            error_message = f"Rule index {rule_index}: Rule section is invalid"
        
        if not error_message:
            existing_rules = CheckpointRule.objects.filter(policy__policy=policy)
            
            for rule in existing_rules:
                existing_source = json.loads(rule.source)
                existing_destination = json.loads(rule.destination)
                existing_protocol = json.loads(rule.protocol)
                
                protocol_subset = all(p in existing_protocol for p in protocol)
                
                source_subset = True
                for s in source:
                    if s not in existing_source:
                        if is_ipaddress(s):
                            source_subset = any(
                                ip_in_network(s, es) if is_subnet(es)
                                else ip_in_range(s, es) if is_ip_range(es)
                                else False
                                for es in existing_source
                            )
                        elif is_subnet(s):
                            source_subset = any(
                                network_in_network(s, es) if is_subnet(es)
                                else False
                                for es in existing_source
                            )
                        elif is_ip_range(s):
                            source_subset = any(
                                range_in_range(s, es) if is_ip_range(es)
                                else range_in_network(s, es) if is_subnet(es)
                                else False
                                for es in existing_source
                            )
                        else:
                            source_subset = False
                        
                        if not source_subset:
                            break
                
                destination_subset = True
                for d in destination:
                    if d not in existing_destination:
                        if is_ipaddress(d):
                            destination_subset = any(
                                ip_in_network(d, ed) if is_subnet(ed)
                                else ip_in_range(d, ed) if is_ip_range(ed)
                                else False
                                for ed in existing_destination
                            )
                        elif is_subnet(d):
                            destination_subset = any(
                                network_in_network(d, ed) if is_subnet(ed)
                                else False
                                for ed in existing_destination
                            )
                        elif is_ip_range(d):
                            destination_subset = any(
                                range_in_range(d, ed) if is_ip_range(ed)
                                else range_in_network(d, ed) if is_subnet(ed)
                                else False
                                for ed in existing_destination
                            )
                        else:
                            destination_subset = False
                        
                        if not destination_subset:
                            break
                
                if source_subset and destination_subset and protocol_subset:
                    error_message = (f"Rule index {rule_index}: Duplicate rule detected! Existing rule ID: {rule.id}")
                    break
    
    return error_message

def check_update_local_user_input(data, index):
    rule_index = index + 1
    error_message = str()
    if data != []:
        note = data[3]
        if note == "":
            error_message = f"Rule index {rule_index}: Note can not be empty"
    return error_message
