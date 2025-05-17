from ipaddress import IPv4Address
from ipaddress import ip_network
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


def check_list_object(datalist):
    for item in datalist:
        if item != "any" and is_ipaddress(item) is True:
            pass
        elif item != "any" and is_subnet(item) is True:
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
        source = [i.replace(" ", "").replace("\r", "") for i in data[3].split("\n")]
        destination = [
            i.replace(" ", "").replace("\r", "") for i in data[4].split("\n")
        ]
        protocol = [i.replace(" ", "").replace("\r", "") for i in data[5].split("\n")]
        section = data[7]
        
        if policy == "":
            error_message = f"Rule index {rule_index}: Policy template name can not be empty"
        elif rule_name == "":
            error_message = f"Rule index {rule_index}: Policy template rule_name can not be empty"
        elif source == [""]:
            error_message = f"Rule index {rule_index}: Source address is invalid"
        elif "any" in source and len(source) > 1:
            error_message = f"Rule index {rule_index}: Source address is invalid"
        elif not check_list_object(source):
            error_message = f"Rule index {rule_index}: Source address is invalid"
        elif destination == [""]:
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
            normalized_source = json.dumps(sorted(source))
            normalized_destination = json.dumps(sorted(destination))
            normalized_protocol = json.dumps(sorted(protocol))
            
            duplicate_rules = CheckpointRule.objects.filter(
                source=normalized_source,
                destination=normalized_destination,
                protocol=normalized_protocol,
                policy__policy=policy  
            )
            
            if duplicate_rules.exists():
                duplicate_ids = ", ".join(str(rule.id) for rule in duplicate_rules)
                error_message = (f"Rule index {rule_index}: Duplicate rule detected! "
                               f"Existing rule ID(s): {duplicate_ids}")
    
    return error_message


def check_update_local_user_input(data, index):
    rule_index = index + 1
    error_message = str()
    if data != []:
        note = data[3]
        if note == "":
            error_message = f"Rule index {rule_index}: Note can not be empty"
    return error_message
