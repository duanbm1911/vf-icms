from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group
from src.cm.checkpoint.func import *
from src.cm.f5.func import check_create_vs_input
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q
from inventory.models import *
from ipplan.models import *
from src.ipplan.func import *
from src.cm.checkpoint.func import *
from src.cm.fmc.func import *
from cm.models import *
from ipaddress import ip_network
from django.db.models import Count
from operator import itemgetter
from dotenv import load_dotenv
from django.db import transaction
import datetime
import base64
import json

load_dotenv()

# Create your views here.


def replace_characters(string):
    new_string = (
        str(string)
        .replace("<", "%")
        .replace(">", "%")
        .replace("?", "%")
        .replace("!", "%")
        .replace("(", "%")
        .replace(")", "%")
        .replace("&", "%")
        .replace("+", "%")
        .replace("\\", "%")
    )
    return new_string


def view_or_basicauth(view, request, test_func, realm="", *args, **kwargs):

    if test_func(request.user):
        return view(request, *args, **kwargs)

    if "HTTP_AUTHORIZATION" in request.META:
        auth = request.META["HTTP_AUTHORIZATION"].split()
        if len(auth) == 2:

            if auth[0].lower() == "basic":
                string = auth[1].encode("utf-8")
                secret = base64.b64decode(string).decode("utf-8")
                uname, passwd = secret.split(":")
                user = authenticate(username=uname, password=passwd)
                if (
                    user is not None
                    and User.objects.filter(username=uname, groups__name="API").count()
                    > 0
                ):
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        return view(request, *args, **kwargs)

    response = HttpResponse()
    response.status_code = 401
    response["WWW-Authenticate"] = 'Basic realm="%s"' % realm
    return response


def logged_in_or_basicauth(realm=""):
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(
                func, request, lambda u: u.is_authenticated, realm, *args, **kwargs
            )

        return wrapper

    return view_decorator


def has_perm_or_basicauth(perm, realm=""):
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(
                func, request, lambda u: u.has_perm(perm), realm, *args, **kwargs
            )

        return wrapper

    return view_decorator


@login_required()
def inventory_dashboard_01(request):

    device_os_count = list()
    list_device_os = list(DeviceOS.objects.values_list("device_os", flat=True))
    for obj in list_device_os:
        count = Device.objects.filter(device_os__device_os=obj).count()
        device_os_count.append(
            {
                "label": str(obj),
                "y": count,
                "toolTipContent": f"{replace_characters(obj)}:{count}",
            }
        )
    return JsonResponse({"data": device_os_count})


@login_required()
def inventory_dashboard_02(request):
    """
    This dashboard will be display count of device by vendor
    """
    vendor_count = list()
    list_vendor = list(DeviceVendor.objects.values_list(
        "device_vendor", flat=True))
    for obj in list_vendor:
        count = Device.objects.filter(device_vendor__device_vendor=obj).count()
        vendor_count.append(
            {
                "label": str(obj),
                "y": count,
                "toolTipContent": f"{replace_characters(obj)}:{count}",
            }
        )
    return JsonResponse({"data": vendor_count})


@login_required()
def inventory_dashboard_04(request):
    """
    This dashboard will be display count of device by vendor
    """
    type_count = list()
    list_vendor = list(DeviceType.objects.values_list(
        "device_type", flat=True))
    for obj in list_vendor:
        count = Device.objects.filter(device_type__device_type=obj).count()
        type_count.append(
            {
                "label": str(obj),
                "y": count,
                "toolTipContent": f"{replace_characters(obj)}:{count}",
            }
        )
    return JsonResponse({"data": type_count})


@login_required()
def inventory_dashboard_05(request):
    """
    This dashboard will be display count of device by vendor
    """
    location_count = list()
    list_location = list(
        DeviceProvince.objects.values_list("device_province", flat=True)
    )
    for obj in list_location:
        count = Device.objects.filter(
            device_province__device_province=obj).count()
        location_count.append(
            {
                "label": str(obj),
                "y": count,
                "toolTipContent": f"{replace_characters(obj)}:{count}",
            }
        )
    return JsonResponse({"data": location_count})


@login_required()
def inventory_dashboard_06(request):
    """
    This dashboard will be display count of incorrect firmware by device type
    """
    list_device_firmware = Device.objects.all().values_list(
        "device_name", "device_ip", "device_type__device_type", "device_firmware"
    )
    list_firmware = DeviceFirmware.objects.all().values_list(
        "device_type__device_type", "firmware"
    )
    list_device_type = DeviceType.objects.all().values_list("device_type", flat=True)
    datalist01 = list()
    datalist02 = list()
    for item in list_device_firmware:
        device_type = item[2]
        device_firmware = item[3]
        if device_firmware is not None:
            checklist = [
                i for i in list_firmware if i == (device_type, device_firmware)
            ]
            if not checklist:
                datalist01.append(device_type)
    for item in list_device_type:
        count = datalist01.count(item)
        datalist02.append(
            {
                "label": str(item),
                "y": count,
                "toolTipContent": f"{replace_characters(item)}:{count}",
            }
        )
    return JsonResponse({"data": datalist02})


@login_required()
def inventory_dashboard_07(request):
    data_point_01 = list()
    data_point_02 = list()
    data_point_03 = list()
    data_point_04 = list()
    list_data_point = [
        {"name": data_point_01, "desc": "End MA"},
        {"name": data_point_02, "desc": "End License"},
        {"name": data_point_03, "desc": "End HW SP"},
        {"name": data_point_04, "desc": "End SW SP"},
    ]
    datepoint01 = datetime.date.today()
    datepoint02 = datetime.date.today() + datetime.timedelta(days=180)
    list_device_type = DeviceType.objects.all().values_list("device_type", flat=True)
    chart_data = list()
    for device_type in list_device_type:
        obj = DeviceType.objects.get(device_type=device_type)
        point_01 = DeviceManagement.objects.filter(
            device_ip__device_type=obj,
            end_ma_date__gte=datepoint01,
            end_ma_date__lte=datepoint02,
        ).count()
        point_02 = DeviceManagement.objects.filter(
            device_ip__device_type=obj,
            end_license_date__gte=datepoint01,
            end_license_date__lte=datepoint02,
        ).count()
        point_03 = DeviceManagement.objects.filter(
            device_ip__device_type=obj,
            end_sw_support_date__gte=datepoint01,
            end_sw_support_date__lte=datepoint02,
        ).count()
        point_04 = DeviceManagement.objects.filter(
            device_ip__device_type=obj,
            end_hw_support_date__gte=datepoint01,
            end_hw_support_date__lte=datepoint02,
        ).count()
        data_point_01.append(
            {
                "label": device_type,
                "y": point_01,
                "toolTipContent": f"{replace_characters(obj)} - End MA:{point_01}",
            }
        )
        data_point_02.append(
            {
                "label": device_type,
                "y": point_02,
                "toolTipContent": f"{replace_characters(obj)} - End License:{point_02}",
            }
        )
        data_point_03.append(
            {
                "label": device_type,
                "y": point_03,
                "toolTipContent": f"{replace_characters(obj)} - End HW SP:{point_03}",
            }
        )
        data_point_04.append(
            {
                "label": device_type,
                "y": point_04,
                "toolTipContent": f"{replace_characters(obj)} - End SW SP:{point_04}",
            }
        )
    list_data_point = [
        {"name": data_point_01, "desc": "End MA"},
        {"name": data_point_02, "desc": "End License"},
        {"name": data_point_03, "desc": "End HW SP"},
        {"name": data_point_04, "desc": "End SW SP"},
    ]
    for data_point in list_data_point:
        chart_data.append(
            {
                "type": "line",
                "showInLegend": "true",
                "name": data_point["desc"],
                "markerSize": 0,
                "markerType": "square",
                "dataPoints": data_point["name"],
            }
        )
    return JsonResponse({"data": chart_data})


@login_required()
def ipplan_dashboard_01(request):
    """
    This dashboard will be display count of location by regoin
    """
    location_count = list()
    list_region = list(Region.objects.values_list("region", flat=True))
    for obj in list_region:
        count = Location.objects.filter(region__region=obj).count()
        location_count.append(
            {
                "label": str(obj),
                "y": count,
                "toolTipContent": f"{replace_characters(obj)}:{count}",
            }
        )
    return JsonResponse({"data": location_count})


@login_required()
def ipplan_dashboard_02(request):
    """
    This dashboard will be display count of subnet by location
    """
    subnet_count = list()
    list_location = list(Location.objects.values_list("location", flat=True))
    for obj in list_location:
        count = SubnetGroup.objects.filter(location__location=obj).count()
        subnet_count.append(
            {
                "label": str(obj),
                "y": count,
                "toolTipContent": f"{replace_characters(obj)}:{count}",
            }
        )
    return JsonResponse({"data": subnet_count})


@login_required()
def ipplan_dashboard_03(request):
    datalist = list()
    subnets = Subnet.objects.all().values_list("subnet", flat=True)
    for subnet in subnets:
        count_total_ip = len([str(i) for i in ip_network(subnet).hosts()])
        count_used_ip = IpAddressModel.objects.filter(
            subnet__subnet=subnet, inused=True
        ).count()
        percent = round(int(count_used_ip) / int(count_total_ip) * 100, 2)
        datalist.append(
            {
                "label": str(subnet),
                "y": percent,
                "toolTipContent": f"{replace_characters(subnet)} - {percent}% - (Used: {count_used_ip} IPs)",
            }
        )
    datalist = sorted(datalist, key=lambda x: x["y"], reverse=False)[-20:]
    return JsonResponse({"data": datalist})


@login_required()
def ipplan_get_list_ip_available(request):
    subnet = request.GET.get("subnet", None)
    if is_subnet(subnet):
        list_ip_used = list(IpAddressModel.objects.filter(
            subnet__subnet=subnet).values_list("ip", flat=True))
        subnet = ip_network(subnet).hosts()
        ip_available = [str(ip)
                        for ip in subnet if str(ip) not in list_ip_used]
        return JsonResponse({"status": "success", "data": ip_available})
    else:
        return JsonResponse({"status": "failed", "error": "Subnet is invalid"})


@csrf_exempt
@logged_in_or_basicauth()
def ipplan_update_ip_status(request):
    if request.method == "POST":
        dataset = json.loads(request.body.decode("utf-8"))
        for subnet, results in dataset.items():
            subnet_check_count = Subnet.objects.filter(subnet=subnet).count()
            if subnet_check_count > 0:
                for result in results:
                    subnet_obj = Subnet.objects.get(subnet=subnet)
                    ip_check_count = IpAddressModel.objects.filter(
                        ip=result["ip"]
                    ).count()
                    if ip_check_count > 0:
                        if result["status"] == "success":
                            IpAddressModel.objects.update_or_create(
                                ip=result["ip"],
                                defaults={
                                    "subnet": subnet_obj,
                                    "status": result["status"],
                                    "inused": result["inused"],
                                },
                            )
                        else:
                            IpAddressModel.objects.update_or_create(
                                ip=result["ip"],
                                defaults={
                                    "subnet": subnet_obj,
                                    "status": result["status"],
                                },
                            )
                    else:
                        IpAddressModel.objects.update_or_create(
                            ip=result["ip"],
                            defaults={
                                "subnet": subnet_obj,
                                "status": result["status"],
                                "inused": result["inused"],
                                "description": "Discovered automatically",
                                "user_created": str(request.user),
                            },
                        )
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@logged_in_or_basicauth()
def ipplan_get_list_subnet(request):
    if request.method == "GET":
        datalist = list(Subnet.objects.all().values_list("subnet", flat=True))
        return JsonResponse({"datalist": datalist}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@logged_in_or_basicauth()
def get_list_device(request):
    if request.method == "GET":
        datalist = list()
        queryset = Device.objects.all()
        if len(queryset) > 0:
            for item in queryset:
                datalist.append(
                    {
                        "device_ip": item.device_ip,
                        "device_name": item.device_name,
                        "device_os": item.device_os.device_os,
                        "device_category": item.device_category.device_category,
                        "device_vendor": item.device_vendor.device_vendor,
                    }
                )
        return JsonResponse({"datalist": datalist}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@csrf_exempt
@logged_in_or_basicauth()
def update_device_firmware(request):
    if request.method == "POST":
        dataset = request.POST.dict()
        for device_ip, firmware in dataset.items():
            Device.objects.update_or_create(
                device_ip=device_ip, defaults={"device_firmware": firmware}
            )
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


def device_report():
    queryset_01 = DeviceManagement.objects.all()
    count_01 = queryset_01.count()
    countlist = list()
    list_device_vendor = DeviceVendor.objects.filter().values_list(
        "device_vendor", flat=True
    )
    for device_vendor in list_device_vendor:
        count = DeviceManagement.objects.filter(
            device_ip__device_vendor__device_vendor=device_vendor
        ).count()
        countlist.append({"device_vendor": device_vendor, "count": count})
    countlist = sorted(countlist, key=itemgetter('count'), reverse=True)
    datalist = {"device_count": count_01, "count_by_vendor": countlist}
    return datalist


def device_management_report():
    datalist = list()
    datepoint01 = datetime.date.today()
    datepoint02 = datetime.date.today() + datetime.timedelta(days=180)
    count_01 = DeviceManagement.objects.filter(
        end_ma_date__gte=datepoint01, end_ma_date__lte=datepoint02
    ).count()
    count_02 = DeviceManagement.objects.filter(
        end_license_date__gte=datepoint01, end_license_date__lte=datepoint02
    ).count()
    count_03 = DeviceManagement.objects.filter(
        end_sw_support_date__gte=datepoint01, end_sw_support_date__lte=datepoint02
    ).count()
    count_04 = DeviceManagement.objects.filter(
        end_hw_support_date__gte=datepoint01, end_hw_support_date__lte=datepoint02
    ).count()
    datalist = {
        "list_end_ma": count_01,
        "list_end_license": count_02,
        "list_end_sw_sp": count_03,
        "list_end_hw_sp": count_04,
    }
    return datalist


def device_firmmware_report():
    list_device_firmware = Device.objects.all().values_list(
        "device_name", "device_ip", "device_type__device_type", "device_firmware", "device_province__device_province"
    )
    list_firmware = DeviceFirmware.objects.all().values_list(
        "device_type__device_type", "firmware"
    )
    list_device_type = DeviceType.objects.all().values_list("device_type", flat=True)
    list_device_province = DeviceProvince.objects.all(
    ).values_list("device_province", flat=True)
    datalist01 = list()
    datalist02 = list()
    for item in list_device_firmware:
        device_type = item[2]
        device_firmware = item[3]
        device_province = item[4]
        if device_firmware is not None:
            checklist = [
                i for i in list_firmware if i == (device_type, device_firmware)
            ]
            if not checklist:
                datalist01.append(device_province)
    for device_province in list_device_province:
        count = datalist01.count(device_province)
        if count != 0:
            datalist02.append(
                {"device_province": device_province, "count": count})
    return sorted(datalist02, key=itemgetter('count'), reverse=True)


@logged_in_or_basicauth()
def inventory_report(request):
    device = device_report()
    device_management = device_management_report()
    device_firmmware = device_firmmware_report()
    data = {
        "device": device,
        "device_management": device_management,
        "device_firmmware": device_firmmware,
    }
    return JsonResponse({"data": data})


@csrf_exempt
@logged_in_or_basicauth()
def update_device_status(request):
    if request.method == "POST":
        dataset = json.loads(request.body.decode("utf-8"))
        for device_ip, status in dataset.items():
            checklist = Device.objects.filter(device_ip=device_ip).count()
            if checklist > 0:
                model = Device.objects.filter(device_ip=device_ip)
                model.update(device_status=status)
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@login_required()
@csrf_exempt
def cm_checkpoint_create_rule(request):
    try:
        if request.user.groups.filter(name="ADMIN").exists():
            if request.method == "POST":
                list_obj = list(request.POST)
                list_error_message = str()
                datalist = list()
                user_created = request.user
                for obj in list_obj:
                    index = list_obj.index(obj)
                    data = request.POST.getlist(obj)
                    error_message = check_cp_access_rule_input(data, index)
                    if not error_message:
                        policy = data[0]
                        gateway = data[1].split(",")
                        description = data[2].replace(" ", "-")
                        source = [
                            i.replace(" ", "").replace("\r", "")
                            for i in data[3].split("\n")
                        ]
                        destination = [
                            i.replace(" ", "").replace("\r", "")
                            for i in data[4].split("\n")
                        ]
                        protocol = [
                            i.replace(" ", "").replace("\r", "")
                            for i in data[5].split("\n")
                        ]
                        schedule = data[6]
                        section = data[7]
                        datalist.append(
                            [
                                policy,
                                json.dumps(gateway),
                                description,
                                json.dumps(source),
                                json.dumps(destination),
                                json.dumps(protocol),
                                section,
                                schedule,
                                user_created,
                            ]
                        )
                    else:
                        list_error_message += error_message + "\n"
                if list_error_message:
                    return JsonResponse(
                        {"status": "failed", "message": list_error_message}, status=200
                    )
                else:
                    for item in datalist:
                        model = CheckpointRule(
                            policy=CheckpointPolicy.objects.get(
                                policy=item[0]),
                            gateway=item[1],
                            description=item[2],
                            source=item[3],
                            destination=item[4],
                            protocol=item[5],
                            section=item[6],
                            schedule=item[7],
                            user_created=item[8],
                        )
                        model.save()
                    return JsonResponse(
                        {"status": "success", "message": "Create rule success"},
                        status=200,
                    )
            else:
                return JsonResponse(
                    {"status": "failed", "message": "Request method is not allowed"},
                    status=405,
                )
        else:
            return JsonResponse({"erorr": "forbidden"}, status=403)
    except Exception as error:
        return JsonResponse(
            {"status": "failed", "message": f"Exception error: {error}"}, status=500
        )


@login_required()
def cm_checkpoint_get_list_policy(request):
    if request.user.groups.filter(name="ADMIN").exists():
        if request.method == "GET":
            site = request.GET.get("site", None)
            if site is None:
                datalist = CheckpointPolicy.objects.all().values_list(
                    "policy", flat=True
                )
            else:
                datalist = CheckpointPolicy.objects.filter(site__site=site).values_list(
                    "policy", flat=True
                )
            return JsonResponse({"data": list(datalist)}, status=200)
        else:
            return JsonResponse({"erorr": "Method is not allowed"}, status=405)
    else:
        return JsonResponse({"erorr": "forbidden"}, status=403)


def cm_checkpoint_get_list_gateway(request):
    if request.user.groups.filter(name="ADMIN").exists():
        datalist = []
        if request.method == "GET":
            policy = request.GET.get("policy", None)
            if policy:
                try:
                    object = CheckpointPolicy.objects.get(policy=policy)
                except CheckpointPolicy.DoesNotExist:
                    return JsonResponse({"erorr": f"Policy name: {policy} dose not exists"}, status=401)
                else:
                    objects = CheckpointGateway.objects.filter(
                        policy__policy=policy).values_list('gateway', flat=True)

                    for item in list(objects):
                        datalist.append({"id": item, "label": item})
                    return JsonResponse({"datalist": list(datalist)}, status=200)
            else:
                return JsonResponse({"erorr": f"Policy parameter is missing"}, status=401)
        else:
            return JsonResponse({"erorr": "Method is not allowed"}, status=405)
    else:
        return JsonResponse({"erorr": "forbidden"}, status=403)


@csrf_exempt
@logged_in_or_basicauth()
def cm_checkpoint_update_rule_section(request):
    if request.method == "POST":
        dataset = json.loads(request.body.decode("utf-8"))
        for policy, list_rule_section in dataset.items():
            checklist = CheckpointPolicy.objects.filter(policy=policy).count()
            if checklist > 0:
                for rule_section in list_rule_section:
                    obj = CheckpointPolicy.objects.get(policy=policy)
                    CheckpointRuleSection.objects.update_or_create(
                        policy=obj, section=rule_section
                    )
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_checkpoint_get_list_rule_section(request):
    if request.method == "GET":
        datalist = list()
        policy = request.GET.get("policy", None)
        datalist = CheckpointRuleSection.objects.filter(
            policy__policy=policy
        ).values_list("section", flat=True)
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_checkpoint_get_list_site(request):
    if request.method == "GET":
        datalist = list()
        list_smc = CheckpointSite.objects.all()
        for item in list_smc:
            data = {}
            list_policy = CheckpointPolicy.objects.filter(
                site__smc=item.smc
            ).values_list("policy", flat=True)
            data["smc"] = item.smc
            data["site"] = item.site
            data["policy"] = list(list_policy)
            datalist.append(data)
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_checkpoint_get_list_rule(request):
    if request.method == "GET":
        data = dict()
        list_site = CheckpointPolicy.objects.all().values_list(
            "site__site", "site__smc", "layer"
        )
        list_site = [list(i) for i in list_site]
        if list_site:
            for item in list_site:
                rules = CheckpointRule.objects.filter(
                    Q(status="Created") | Q(status="Install-Only"),
                    policy__site__site=item[0],
                ).values_list(
                    "id",
                    "policy__policy",
                    "gateway",
                    "description",
                    "source",
                    "destination",
                    "protocol",
                    "section",
                    "schedule",
                    "status",
                )
                rules = [list(i) for i in rules]
                if rules:
                    for obj in rules:
                        obj[2] = json.loads(obj[2])
                        obj[4] = json.loads(obj[4])
                        obj[5] = json.loads(obj[5])
                        obj[6] = json.loads(obj[6])
                        obj.append(item[2])
                site = item[0]
                data[site] = {"smc": item[1], "rules": rules}
        return JsonResponse({"data": data}, status=200)
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@csrf_exempt
@logged_in_or_basicauth()
def cm_checkpoint_update_rule_status(request):
    if request.method == "POST":
        dataset = request.POST.dict()
        rule_id = dataset["rule_id"]
        status = dataset["status"]
        message = dataset["message"]
        model = CheckpointRule.objects.filter(id=rule_id)
        model.update(status=status, message=message)
        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_f5_get_list_device(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "Forbidden"}, status=403)
    
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        datalist = list(F5Device.objects.all().values_list("f5_device_ip", flat=True))
        return JsonResponse({"status": "success", "datalist": datalist})
    except Exception as e:
        return JsonResponse({"error": "Database error"}, status=500)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_create_task_virtual_server(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "Forbidden"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        datalist = []
        error_messages = []
        
        for obj in request.POST:
            data = request.POST.getlist(obj)
            error_message = check_create_vs_input(data, list(request.POST).index(obj))
            
            if error_message:
                error_messages.append(error_message)
                continue
            
            pool_member = [
                member.strip() for member in data[3].split("\n") 
                if member.strip()
            ]
            irules = [rule.strip() for rule in data[8].split(",") if rule.strip()] if data[8] else []
            
            datalist.append({
                'f5_device_ip': data[0],
                'service_name': data[1],
                'virtual_server': data[2],
                'pool_member': pool_member,
                'pool_monitor': data[4],
                'pool_lb_method': data[5],
                'client_ssl_profile': data[6],
                'server_ssl_profile': data[7],
                'irules': irules,
                'waf_profile': data[9],
                'f5_template': data[10],
            })
        
        if error_messages:
            return JsonResponse({
                "status": "failed", 
                "message": "\n".join(error_messages)
            })
        
        f5_devices = {item['f5_device_ip']: F5Device.objects.get(f5_device_ip=item['f5_device_ip']) for item in datalist}
        f5_templates = {item['f5_template']: F5Template.objects.get(template_name=item['f5_template']) for item in datalist}
        
        virtual_servers = []
        for item in datalist:
            vs_ip, vs_port = item['virtual_server'].split(":")
            service_name = item['service_name']
            
            virtual_servers.append(F5CreateVirtualServer(
                f5_device_ip=f5_devices[item['f5_device_ip']],
                service_name=service_name,
                vs_ip=vs_ip,
                vs_port=vs_port,
                vs_name=f"{service_name}-{vs_ip}-{vs_port}-vs",
                pool_name=f"{service_name}-{vs_ip}-{vs_port}-pool",
                pool_member=json.dumps(item['pool_member']),
                pool_monitor=item['pool_monitor'],
                pool_lb_method=item['pool_lb_method'],
                client_ssl_profile=item['client_ssl_profile'],
                server_ssl_profile=item['server_ssl_profile'],
                irules=json.dumps(item['irules']),
                waf_profile=item['waf_profile'],
                f5_template=f5_templates[item['f5_template']],
                status="Created",
                user_created=request.user,
            ))
        
        F5CreateVirtualServer.objects.bulk_create(virtual_servers)
        
        return JsonResponse({
            "status": "success",
            "message": "Create virtual server success"
        })
        
    except F5Device.DoesNotExist:
        return JsonResponse({"error": "F5 device not found"}, status=400)
    except F5Template.DoesNotExist:
        return JsonResponse({"error": "F5 template not found"}, status=400)
    except Exception as e:
        return JsonResponse({"error": "Database error"}, status=500)


@logged_in_or_basicauth()
def cm_f5_get_list_client_ssl_profile(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    f5_device_ip = request.GET.get("f5_device_ip")
    if not f5_device_ip:
        return JsonResponse({"error": "f5_device_ip parameter required"}, status=400)
    
    try:
        datalist = list(F5ClientSSLProfile.objects.filter(
            f5_device_ip__f5_device_ip=f5_device_ip
        ).values_list("profile_name", flat=True))
        
        return JsonResponse({"status": "success", "datalist": datalist})
    except Exception as e:
        return JsonResponse({"error": "Database error"}, status=500)


@logged_in_or_basicauth()
def cm_f5_get_list_virtual_server(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    f5_device_ip = request.GET.get("f5_device_ip")
    if not f5_device_ip:
        return JsonResponse({"error": "f5_device_ip parameter required"}, status=400)
    
    try:
        user_groups = set(request.user.groups.all())
        objects = F5VirtualServer.objects.filter(
            f5_device_ip__f5_device_ip=f5_device_ip
        ).prefetch_related('group_permission')
        
        datalist = [
            obj.vs_name for obj in objects
            if set(obj.group_permission.all()) & user_groups
        ]
        
        return JsonResponse({"status": "success", "datalist": datalist})
    except Exception as e:
        return JsonResponse({"error": "Database error"}, status=500)


@logged_in_or_basicauth()
def cm_f5_get_list_server_ssl_profile(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    f5_device_ip = request.GET.get("f5_device_ip")
    if not f5_device_ip:
        return JsonResponse({"error": "f5_device_ip parameter required"}, status=400)
    
    try:
        datalist = list(F5ServerSSLProfile.objects.filter(
            f5_device_ip__f5_device_ip=f5_device_ip
        ).values_list("profile_name", flat=True))
        
        return JsonResponse({"status": "success", "datalist": datalist})
    except Exception as e:
        return JsonResponse({"error": "Database error"}, status=500)


@logged_in_or_basicauth()
def cm_f5_get_list_pool_monitor(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    f5_device_ip = request.GET.get("f5_device_ip")
    if not f5_device_ip:
        return JsonResponse({"error": "f5_device_ip is required"}, status=400)
    
    datalist = F5PoolMemberMonitor.objects.filter(
        f5_device_ip__f5_device_ip=f5_device_ip
    ).values_list("pool_monitor", flat=True)
    
    return JsonResponse({"status": "success", "datalist": list(datalist)})


@logged_in_or_basicauth()
def cm_f5_get_list_pool_lb_method(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    datalist = F5PoolMemberMethod.objects.all().values_list(
        "pool_method", flat=True
    )
    
    return JsonResponse({"status": "success", "datalist": list(datalist)})


@logged_in_or_basicauth()
def cm_f5_get_list_template(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    datalist = F5Template.objects.all().values_list("template_name", flat=True)
    
    return JsonResponse({"status": "success", "datalist": list(datalist)})


@logged_in_or_basicauth()
def cm_f5_get_list_waf_profile(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    f5_device_ip = request.GET.get("f5_device_ip")
    if not f5_device_ip:
        return JsonResponse({"error": "f5_device_ip is required"}, status=400)
    
    datalist = F5WafProfile.objects.filter(
        f5_device_ip__f5_device_ip=f5_device_ip
    ).values_list("waf_profile", flat=True)
    
    return JsonResponse({"status": "success", "datalist": list(datalist)})


@logged_in_or_basicauth()
def cm_f5_get_list_irule_profile(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    f5_device_ip = request.GET.get("f5_device_ip")
    if not f5_device_ip:
        return JsonResponse({"error": "f5_device_ip is required"}, status=400)
    
    irule_names = F5Irule.objects.filter(
        f5_device_ip__f5_device_ip=f5_device_ip
    ).values_list("irule_name", flat=True)
    
    datalist = [{"id": name, "label": name} for name in irule_names]
    
    return JsonResponse({"status": "success", "datalist": datalist})


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_client_ssl_profile(request):
    if request.method != "POST":
        return JsonResponse({"error_message": "method not allowed"}, status=405)
    
    try:
        dataset = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error_message": "invalid JSON"}, status=400)
    
    f5_devices = {ip: device for ip, device in F5Device.objects.filter(
        f5_device_ip__in=dataset.keys()).values_list('f5_device_ip', 'id')}
    
    for f5_device_ip, list_client_ssl_profile in dataset.items():
        if f5_device_ip not in f5_devices:
            continue
            
        device_obj = F5Device.objects.get(pk=f5_devices[f5_device_ip])
        
        for client_ssl_profile in list_client_ssl_profile:
            F5ClientSSLProfile.objects.update_or_create(
                f5_device_ip=device_obj, profile_name=client_ssl_profile
            )
    
    return JsonResponse({"status": "success"}, status=200)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_server_ssl_profile(request):
    if request.method != "POST":
        return JsonResponse({"error_message": "method not allowed"}, status=405)
    
    try:
        dataset = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error_message": "invalid JSON"}, status=400)
    
    f5_devices = {ip: device for ip, device in F5Device.objects.filter(
        f5_device_ip__in=dataset.keys()).values_list('f5_device_ip', 'id')}
    
    for f5_device_ip, list_server_ssl_profile in dataset.items():
        if f5_device_ip not in f5_devices:
            continue
            
        device_obj = F5Device.objects.get(pk=f5_devices[f5_device_ip])
        
        for server_ssl_profile in list_server_ssl_profile:
            F5ServerSSLProfile.objects.update_or_create(
                f5_device_ip=device_obj, profile_name=server_ssl_profile
            )
    
    return JsonResponse({"status": "success"}, status=200)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_irule_profile(request):
    if request.method != "POST":
        return JsonResponse({"error_message": "method not allowed"}, status=405)
    
    try:
        dataset = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error_message": "invalid JSON"}, status=400)
    
    f5_devices = {ip: device for ip, device in F5Device.objects.filter(
        f5_device_ip__in=dataset.keys()).values_list('f5_device_ip', 'id')}
    
    for f5_device_ip, list_irule_profile in dataset.items():
        if f5_device_ip not in f5_devices:
            continue
            
        device_obj = F5Device.objects.get(pk=f5_devices[f5_device_ip])
        
        for irule_profile in list_irule_profile:
            F5Irule.objects.update_or_create(
                f5_device_ip=device_obj, irule_name=irule_profile
            )
    
    return JsonResponse({"status": "success"}, status=200)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_waf_profile(request):
    if request.method != "POST":
        return JsonResponse({"error_message": "method not allowed"}, status=405)
    
    try:
        dataset = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error_message": "invalid JSON"}, status=400)
    
    f5_devices = {ip: device for ip, device in F5Device.objects.filter(
        f5_device_ip__in=dataset.keys()).values_list('f5_device_ip', 'id')}
    
    for f5_device_ip, list_waf_profile in dataset.items():
        if f5_device_ip not in f5_devices:
            continue
            
        device_obj = F5Device.objects.get(pk=f5_devices[f5_device_ip])
        
        for waf_profile in list_waf_profile:
            F5WafProfile.objects.update_or_create(
                f5_device_ip=device_obj, waf_profile=waf_profile
            )
    
    return JsonResponse({"status": "success"}, status=200)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_task_virtual_server(request):
    if request.method != "POST":
        return JsonResponse({"error_message": "method not allowed"}, status=405)
    
    try:
        dataset = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error_message": "invalid JSON"}, status=400)
    
    task_ids = list(dataset.keys())
    existing_ids = set(F5CreateVirtualServer.objects.filter(
        id__in=task_ids).values_list('id', flat=True))
    
    for task_id, (status, message) in dataset.items():
        if int(task_id) in existing_ids:
            F5CreateVirtualServer.objects.filter(id=task_id).update(
                status=status, message=message)
    
    return JsonResponse({"status": "success"}, status=200)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_task_limit_connection(request):
    if request.method != "POST":
        return JsonResponse({"error_message": "method not allowed"}, status=405)
    
    try:
        dataset = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error_message": "invalid JSON"}, status=400)
    
    task_ids = list(dataset.keys())
    existing_ids = set(F5LimitConnection.objects.filter(
        id__in=task_ids).values_list('id', flat=True))
    
    for task_id, (status, message) in dataset.items():
        if int(task_id) in existing_ids:
            F5LimitConnection.objects.filter(id=task_id).update(
                status=status, message=message)
    
    return JsonResponse({"status": "success"}, status=200)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_get_list_task_create_virtual_server(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    objects = F5CreateVirtualServer.objects.select_related('f5_template').filter(status="Created")
    
    datalist = [
        {
            "task_id": obj.id,
            "f5_device_ip": str(obj.f5_device_ip),
            "vs_name": obj.vs_name,
            "vs_ip": obj.vs_ip,
            "vs_port": obj.vs_port,
            "pool_name": obj.pool_name,
            "pool_member": json.loads(obj.pool_member),
            "pool_monitor": obj.pool_monitor,
            "pool_lb_method": obj.pool_lb_method,
            "client_ssl_profile": obj.client_ssl_profile,
            "server_ssl_profile": obj.server_ssl_profile,
            "partition": obj.f5_template.partition,
            "protocol": obj.f5_template.protocol,
            "client_protocol_profile": obj.f5_template.client_protocol_profile,
            "server_protocol_profile": obj.f5_template.server_protocol_profile,
            "client_http_profile": obj.f5_template.client_http_profile,
            "server_http_profile": obj.f5_template.server_http_profile,
            "snat_name": obj.f5_template.snat_name,
            "http_analytics_profile": obj.f5_template.http_analytics_profile,
            "tcp_analytics_profile": obj.f5_template.tcp_analytics_profile,
            "http_compression_profile": obj.f5_template.http_compression_profile,
            "web_acceleration_profile": obj.f5_template.web_acceleration_profile,
            "web_socket_profile": obj.f5_template.web_socket_profile,
            "waf_profile": obj.waf_profile,
            "irules": json.loads(obj.irules) if obj.irules else [],
        }
        for obj in objects
    ]
    
    return JsonResponse({"status": "success", "datalist": datalist})


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_get_list_task_limit_connection(request):
    datalist = list()
    if request.method == "GET":
        objects = F5LimitConnection.objects.filter(status="Created")
        for object in objects:
            datalist.append(
                {
                    "task_id": object.id,
                    "f5_device_ip": object.f5_device_ip.f5_device_ip,
                    "vs_name": object.vs_name,
                    "data": {"connectionLimit": str(object.connection_number)},
                }
            )
        return JsonResponse({"status": "success", "datalist": datalist})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_virtual_server(request):
    if request.method != "POST":
        return JsonResponse({"error_message": "method not allowed"}, status=405)
    
    try:
        dataset = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error_message": "invalid JSON"}, status=400)
    
    f5_devices = {ip: device for ip, device in F5Device.objects.filter(
        f5_device_ip__in=dataset.keys()).values_list('f5_device_ip', 'id')}
    
    admin_group = Group.objects.get(name="ADMIN")
    
    for f5_device_ip, datalist in dataset.items():
        if f5_device_ip not in f5_devices:
            continue
            
        device_obj = F5Device.objects.get(pk=f5_devices[f5_device_ip])
        
        for vs_name, vs_ip, vs_port, client_ssl_profile, server_ssl_profile in datalist:
            obj, created = F5VirtualServer.objects.update_or_create(
                f5_device_ip=device_obj,
                vs_name=vs_name,
                defaults={
                    'vs_ip': vs_ip,
                    'vs_port': vs_port,
                    'client_ssl_profile': client_ssl_profile,
                    'server_ssl_profile': server_ssl_profile
                }
            )
            obj.group_permission.set([admin_group])
    
    return JsonResponse({"status": "success"}, status=200)


@login_required()
def checkpoint_dashboard_01(request):
    results = list()
    status_counts = CheckpointRule.objects.values(
        'status').annotate(count=Count('status'))
    for item in status_counts:
        label = item['status']
        count = item['count']
        results.append(
            {
                "label": label,
                "y": count,
                "toolTipContent": f"{replace_characters(label)}:{count}",
            }
        )
    return JsonResponse({"data": results})


@login_required()
def checkpoint_dashboard_02(request):
    results = list()
    user_counts = CheckpointRule.objects.values(
        'user_created').annotate(count=Count('user_created'))
    for item in user_counts:
        label = item['user_created']
        count = item['count']
        results.append(
            {
                "label": label,
                "y": count,
                "toolTipContent": f"{replace_characters(label)}:{count}",
            }
        )
    return JsonResponse({"data": results})


@login_required()
def fmc_dashboard_01(request):
    results = list()
    status_counts = FMCRule.objects.values(
        'status').annotate(count=Count('status'))
    for item in status_counts:
        label = item['status']
        count = item['count']
        results.append(
            {
                "label": label,
                "y": count,
                "toolTipContent": f"{replace_characters(label)}:{count}",
            }
        )
    return JsonResponse({"data": results})


@login_required()
def fmc_dashboard_02(request):
    results = list()
    user_counts = FMCRule.objects.values(
        'user_created').annotate(count=Count('user_created'))
    for item in user_counts:
        label = item['user_created']
        count = item['count']
        results.append(
            {
                "label": label,
                "y": count,
                "toolTipContent": f"{replace_characters(label)}:{count}",
            }
        )
    return JsonResponse({"data": results})


@login_required()
@csrf_exempt
def cm_fmc_create_rule(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    try:
        post_keys = list(request.POST)
        error_messages = []
        validated_rules = []
        user_created = request.user
        
        for i, key in enumerate(post_keys):
            data = request.POST.getlist(key)
            error_message = check_fmc_access_rule_input(data, i)
            
            if error_message:
                error_messages.append(error_message)
                continue
            
            policy_name = data[1]
            description = data[2].replace(" ", "-")
            source = [
                item.replace(" ", "").replace("\r", "")
                for item in data[3].split("\n")
            ]
            destination = [
                item.replace(" ", "").replace("\r", "")
                for item in data[4].split("\n")
            ]
            protocol = [
                item.replace(" ", "").replace("\r", "")
                for item in data[5].split("\n")
            ]
            schedule = data[6]
            category = data[7]
            
            gateways = FMCGateway.objects.filter(
                policy__policy=policy_name
            ).values_list('gateway', flat=True)
            
            validated_rules.append({
                'policy_name': policy_name,
                'gateway': json.dumps(list(gateways)),
                'description': description,
                'source': json.dumps(source),
                'destination': json.dumps(destination),
                'protocol': json.dumps(protocol),
                'category': category,
                'schedule': schedule,
                'user_created': user_created,
            })
        
        if error_messages:
            return JsonResponse({
                "status": "failed", 
                "message": "\n".join(error_messages)
            }, status=400)
        
        rules_to_create = []
        for rule_data in validated_rules:
            try:
                policy_obj = FMCPolicy.objects.get(policy=rule_data['policy_name'])
            except FMCPolicy.DoesNotExist:
                return JsonResponse({
                    "error": f"Policy '{rule_data['policy_name']}' not found"
                }, status=404)
            
            rules_to_create.append(FMCRule(
                policy=policy_obj,
                gateway=rule_data['gateway'],
                description=rule_data['description'],
                source=rule_data['source'],
                destination=rule_data['destination'],
                protocol=rule_data['protocol'],
                category=rule_data['category'],
                schedule=rule_data['schedule'],
                user_created=rule_data['user_created'],
            ))
        
        FMCRule.objects.bulk_create(rules_to_create)
        
        return JsonResponse({
            "status": "success", 
            "message": "Rules created successfully"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            "error": f"Error creating rules: {str(e)}"
        }, status=500)


@login_required()
def cm_fmc_get_list_policy(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    try:
        site = request.GET.get("site")
        
        if not site:
            return JsonResponse({"error": "Site parameter is required"}, status=400)
        
        policies = FMCPolicy.objects.filter(
            domain__site__site=site
        ).values_list("policy", flat=True)
        
        return JsonResponse({"data": list(policies)}, status=200)
        
    except Exception as e:
        return JsonResponse({"error": f"Error fetching policies: {str(e)}"}, status=500)


@logged_in_or_basicauth()
def cm_checkpoint_get_list_local_user(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    try:
        datalist = []
        sites = CheckpointSite.objects.all()
        
        for site in sites:
            users = CheckpointLocalUser.objects.filter(
                Q(status="Created") | Q(status="Install-Only"), 
                template__site=site
            ).select_related('template')
            
            user_list = []
            for user in users:
                user_groups = [str(group.group) for group in user.user_group.all()]
                
                user_list.append({
                    "id": user.id,
                    "user_name": user.user_name,
                    "is_partner": user.is_partner,
                    "password": user.password,
                    "phone_number": user.phone_number,
                    "email": user.email,
                    "expiration_date": user.expiration_date,
                    "user_group": user_groups,
                    "custom_group": user.custom_group or "",
                    "default_group": user.template.default_group,
                    "radius_group": user.template.radius_group_server,
                    "skip_send_alert_email": user.template.skip_send_alert_email
                })

            datalist.append({
                "smc": site.smc,
                "smc_hostname": site.smc_hostname,
                "users": user_list
            })
            
        return JsonResponse({"data": datalist}, status=200)
        
    except Exception as e:
        return JsonResponse({"error": f"Error fetching users: {str(e)}"}, status=500)


@csrf_exempt
@logged_in_or_basicauth()
def cm_checkpoint_update_local_user(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    try:
        dataset = request.POST.dict()
        
        if not dataset:
            return JsonResponse({"error": "No data provided"}, status=400)
        
        user_id = dataset.get("user_id")
        status = dataset.get("status")
        message = dataset.get("message")
        
        if not all([user_id, status is not None, message is not None]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)
        
        updated_count = CheckpointLocalUser.objects.filter(id=user_id).update(
            status=status, 
            message=message
        )
        
        if updated_count == 0:
            return JsonResponse({"error": "User not found"}, status=404)
            
        return JsonResponse({"status": "success"})
        
    except Exception as e:
        return JsonResponse({"error": f"Error updating user: {str(e)}"}, status=500)


@login_required()
def cm_fmc_get_list_gateway(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    policy = request.GET.get("policy")
    if not policy:
        return JsonResponse({"error": "Policy parameter is required"}, status=400)
    
    try:
        policy_obj = FMCPolicy.objects.get(policy=policy)
        domain = policy_obj.gateway.domain.domain
        
        gateways = FMCGateway.objects.filter(
            domain__domain=domain
        ).values_list('gateway', flat=True)
        
        datalist = [{"id": gateway, "label": gateway} for gateway in gateways]
        return JsonResponse({"datalist": datalist}, status=200)
        
    except FMCPolicy.DoesNotExist:
        return JsonResponse({"error": f"Policy '{policy}' not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Error fetching gateways: {str(e)}"}, status=500)


@csrf_exempt
@logged_in_or_basicauth()
def cm_fmc_update_rule_category(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    try:
        dataset = json.loads(request.body.decode("utf-8"))
        
        if not isinstance(dataset, dict):
            return JsonResponse({"error": "Invalid data format"}, status=400)
        
        for policy_name, rule_categories in dataset.items():
            if not rule_categories or not isinstance(rule_categories, list):
                continue
            
            try:
                policy_obj = FMCPolicy.objects.get(policy=policy_name)
            except FMCPolicy.DoesNotExist:
                return JsonResponse({"error": f"Policy '{policy_name}' not found"}, status=404)
            
            for category in rule_categories:
                FMCRuleCategory.objects.update_or_create(
                    policy=policy_obj,
                    category=category
                )
        
        return JsonResponse({"status": "success"}, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Error updating rule categories: {str(e)}"}, status=500)


@logged_in_or_basicauth()
def cm_fmc_get_list_rule_category(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    policy = request.GET.get("policy")
    if not policy:
        return JsonResponse({"error": "Policy parameter is required"}, status=400)
    
    try:
        categories = FMCRuleCategory.objects.filter(
            policy__policy=policy
        ).values_list("category", flat=True)
        
        return JsonResponse({"status": "success", "datalist": list(categories)})
        
    except Exception as e:
        return JsonResponse({"error": f"Error fetching rule categories: {str(e)}"}, status=500)
    

@logged_in_or_basicauth()
def cm_checkpoint_get_alert_email_template(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    template = request.GET.get("template")
    if not template:
        return JsonResponse({"error": "Template parameter is required"}, status=400)
    
    try:
        obj = CheckpointEmailAlertTemplate.objects.get(template_name=template)
        return JsonResponse({
            "status": "success",
            "email_subject": obj.email_title,
            "email_body": obj.email_body
        })
        
    except CheckpointEmailAlertTemplate.DoesNotExist:
        return JsonResponse({"error": "Template not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Error fetching template: {str(e)}"}, status=500)


@logged_in_or_basicauth()
def cm_fmc_get_list_domain(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    try:
        site = request.GET.get("site")
        
        if site:
            domains = FMCDomain.objects.filter(site__site=site).values_list("domain", flat=True)
        else:
            domains = FMCDomain.objects.values_list("domain", flat=True)
        
        return JsonResponse({"status": "success", "datalist": list(domains)})
        
    except Exception as e:
        return JsonResponse({"error": f"Error fetching domains: {str(e)}"}, status=500)


@csrf_exempt
@logged_in_or_basicauth()
def cm_checkpoint_update_local_user_group(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    try:
        dataset = json.loads(request.body.decode("utf-8"))
        
        if not isinstance(dataset, dict):
            return JsonResponse({"error": "Invalid data format"}, status=400)
        
        for smc, groups in dataset.items():
            if not groups or not isinstance(groups, list):
                continue
                
            try:
                site = CheckpointSite.objects.get(smc=smc)
            except CheckpointSite.DoesNotExist:
                return JsonResponse({"error": f"Site with SMC '{smc}' not found"}, status=404)
            
            for group in groups:
                CheckpointLocalUserGroup.objects.update_or_create(
                    site=site,
                    group=group
                )
        
        return JsonResponse({"status": "success"})
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Error updating user groups: {str(e)}"}, status=500)


@logged_in_or_basicauth()
def cm_fmc_get_list_site(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    try:
        sites = FMCSite.objects.values_list("site", flat=True)
        return JsonResponse({"status": "success", "datalist": list(sites)})
        
    except Exception as e:
        return JsonResponse({"error": f"Error fetching sites: {str(e)}"}, status=500)


@logged_in_or_basicauth()
def cm_fmc_get_list_rule(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    try:
        data = {}
        sites = FMCSite.objects.all().values_list("site", "fmc")
        
        for site_name, fmc in sites:
            rules = FMCRule.objects.filter(
                Q(status="Created") | Q(status="Install-Only"),
                policy__domain__site__site=site_name,
            ).values_list(
                "id", "policy__domain__domain_id", "policy__policy",
                "gateway", "description", "source", "destination",
                "protocol", "category", "schedule", "status",
            )
            
            rule_list = []
            for rule in rules:
                rule_data = list(rule)
                for idx in [3, 5, 6, 7]:
                    rule_data[idx] = json.loads(rule_data[idx]) if rule_data[idx] else None
                rule_list.append(rule_data)
            
            if rule_list:
                data[site_name] = {"fmc": fmc, "rules": rule_list}
        
        return JsonResponse({"data": data}, status=200)
        
    except Exception as e:
        return JsonResponse({"error": f"Error fetching rules: {str(e)}"}, status=500)


@csrf_exempt
@logged_in_or_basicauth()
def cm_fmc_update_rule_status(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    try:
        dataset = request.POST.dict()
        rule_id = dataset.get("rule_id")
        status = dataset.get("status")
        message = dataset.get("message")
        
        updated_count = FMCRule.objects.filter(id=rule_id).update(
            status=status, 
            message=message
        )
        
        if updated_count == 0:
            return JsonResponse({"error": "Rule not found"}, status=404)
            
        return JsonResponse({"status": "success"})
        
    except Exception as e:
        return JsonResponse({"error": f"Error updating rule: {str(e)}"}, status=500)


@login_required()
def cm_checkpoint_get_user_groups(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    template = request.GET.get("template")
    if not template:
        return JsonResponse({"error": "Parameter is required"}, status=401)
    
    try:
        obj = CheckpointLocalUserTemplate.objects.get(name=template)
        groups = CheckpointLocalUserGroup.objects.filter(
            site=obj.site
        ).values_list('group', flat=True)
        
        datalist = [{"id": group, "label": group} for group in groups]
        return JsonResponse({"datalist": datalist}, status=200)
        
    except CheckpointLocalUserTemplate.DoesNotExist:
        return JsonResponse({"error": "Template not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Error fetching user groups: {str(e)}"}, status=500)
    

@csrf_exempt
@logged_in_or_basicauth()
def cm_checkpoint_create_local_user(request):
    try:
        if request.user.groups.filter(name="ADMIN").exists():
            if request.method == "POST":
                list_obj = list(request.POST)
                created_count = 0
                updated_count = 0
                errors = []
                with transaction.atomic():
                    for obj in list_obj:
                        try:
                            index = list_obj.index(obj)
                            data = request.POST.getlist(obj)
                            username = data[0].strip() if data[0] else ""
                            template_name = data[1].strip() if len(data) > 1 and data[1] else ""
                            
                            if not username:
                                errors.append(f"Row {index + 1}: Username is required")
                                continue
                            user_exists = CheckpointLocalUser.objects.filter(user_name=username).exists()
                            if not user_exists and not template_name:
                                errors.append(f"Row {index + 1}: Template is required for new users")
                                continue
                            template = None
                            if template_name:
                                try:
                                    template = CheckpointLocalUserTemplate.objects.get(name=template_name)
                                except CheckpointLocalUserTemplate.DoesNotExist:
                                    errors.append(f"Row {index + 1}: Template '{template_name}' not found")
                                    continue
                            is_partner = data[2].lower() == 'true' if len(data) > 2 and data[2].strip() else False
                            password = data[3].strip() if len(data) > 3 and data[3].strip() else ""
                            email = data[4].strip() if len(data) > 4 and data[4].strip() else ""
                            phone_number = data[5].strip() if len(data) > 5 and data[5].strip() else None
                            custom_group = data[8].strip() if len(data) > 8 and data[8].strip() else ""
                            expiration_date = None
                            if len(data) > 6 and data[6].strip():
                                try:
                                    expiration_date = datetime.datetime.strptime(data[6].strip(), "%Y-%m-%d").date()
                                except ValueError:
                                    errors.append(f"Row {index + 1}: Invalid date format")
                                    continue
                            user_groups = []
                            if len(data) > 7 and data[7].strip():
                                user_groups = [g.strip() for g in data[7].split(',') if g.strip()]
                            user, created = CheckpointLocalUser.objects.get_or_create(
                                user_name=username,
                                defaults={
                                    'user_created': request.user.username,
                                    'template': template,
                                    'is_partner': is_partner,
                                    'password': password,
                                    'email': email,
                                    'phone_number': phone_number,
                                    'expiration_date': expiration_date,
                                    'custom_group': custom_group,
                                    'status': 'Created'
                                }
                            )
                            
                            if created:
                                created_count += 1
                            else:
                                fields_to_update = []
                                if template_name and template and user.template != template:
                                    user.template = template
                                    fields_to_update.append('template')
                                if len(data) > 2 and data[2].strip():
                                    if user.is_partner != is_partner:
                                        user.is_partner = is_partner
                                        fields_to_update.append('is_partner')
                                if len(data) > 3 and data[3].strip():
                                    if user.password != password:
                                        user.password = password
                                        fields_to_update.append('password')
                                if len(data) > 4 and data[4].strip():
                                    if user.email != email:
                                        user.email = email
                                        fields_to_update.append('email')
                                if len(data) > 5 and data[5].strip():
                                    if user.phone_number != phone_number:
                                        user.phone_number = phone_number
                                        fields_to_update.append('phone_number')
                                if len(data) > 6 and data[6].strip():
                                    if user.expiration_date != expiration_date:
                                        user.expiration_date = expiration_date
                                        fields_to_update.append('expiration_date')
                                
                                if len(data) > 8 and data[8].strip():
                                    if user.custom_group != custom_group:
                                        user.custom_group = custom_group
                                        fields_to_update.append('custom_group')
                                if fields_to_update:
                                    user.save(update_fields=fields_to_update)
                                    updated_count += 1
                            if len(data) > 7 and data[7].strip():
                                if user_groups:
                                    groups = []
                                    for group_name in user_groups:
                                        try:
                                            group = CheckpointLocalUserGroup.objects.get(group=group_name)
                                            groups.append(group)
                                        except CheckpointLocalUserGroup.DoesNotExist:
                                            errors.append(f"Row {index + 1}: Group '{group_name}' not found")
                                    if groups:
                                        user.user_group.set(groups)
                        except Exception as e:
                            errors.append(f"Row {index + 1}: {str(e)}")
                if errors:
                    message = f"Created: {created_count}, Updated: {updated_count}\nErrors:\n" + "\n".join(errors)
                    return JsonResponse({"status": "failed", "message": message}, status=200)
                else:
                    message = f"Created: {created_count}, Updated: {updated_count}"
                    return JsonResponse({"status": "success", "message": message}, status=200)
            else:
                return JsonResponse({"status": "failed", "message": "Request method is not allowed"}, status=405)
        else:
            return JsonResponse({"error": "forbidden"}, status=403)
    
    except Exception as error:
        return JsonResponse({"status": "failed", "message": f"Exception error: {error}"}, status=500)
    
@logged_in_or_basicauth()
def cm_checkpoint_get_user_template(request):
    if not request.user.groups.filter(name="ADMIN").exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    
    if request.method != "GET":
        return JsonResponse({"error": "Method is not allowed"}, status=405)
    
    try:
        templates = CheckpointLocalUserTemplate.objects.values_list('name', flat=True)
        return JsonResponse({
            'status': 'success',
            'data': list(templates)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to fetch templates: {e}',
            'data': []
        }, status=500)