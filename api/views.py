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
    if request.user.groups.filter(name="ADMIN").exists():
        if request.method == "GET":
            datalist = F5Device.objects.all().values_list("f5_device_ip", flat=True)
            return JsonResponse(
                {"status": "success", "datalist": list(datalist)}, status=200
            )
        else:
            return JsonResponse(
                {"status": "failed", "erorr": "Method is not allowed"}, status=405
            )
    else:
        return JsonResponse({"status": "failed", "erorr": "forbidden"}, status=403)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_create_task_virtual_server(request):
    try:
        if request.user.groups.filter(name="ADMIN").exists():
            if request.method == "POST":
                list_obj = list(request.POST)
                list_error_message = str()
                datalist = list()
                status = "Created"
                user_created = request.user
                for obj in list_obj:
                    index = list_obj.index(obj)
                    data = request.POST.getlist(obj)
                    error_message = check_create_vs_input(data, index)
                    if not error_message:
                        f5_device_ip = data[0]
                        service_name = data[1]
                        virtual_server = data[2]
                        pool_member = [
                            i.replace(" ", "").replace("\r", "")
                            for i in data[3].split("\n")
                        ]
                        pool_monitor = data[4]
                        pool_lb_method = data[5]
                        client_ssl_profile = data[6]
                        server_ssl_profile = data[7]
                        irules = []
                        if data[8]:
                            irules = [i for i in data[8].split(",")]
                        waf_profile = data[9]
                        f5_template = data[10]
                        datalist.append(
                            [
                                f5_device_ip,
                                service_name,
                                virtual_server,
                                json.dumps(pool_member),
                                pool_monitor,
                                pool_lb_method,
                                client_ssl_profile,
                                server_ssl_profile,
                                json.dumps(irules),
                                waf_profile,
                                f5_template,
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
                        vs_ip = item[2].split(":")[0]
                        vs_port = item[2].split(":")[1]
                        model = F5CreateVirtualServer(
                            f5_device_ip=F5Device.objects.get(
                                f5_device_ip=item[0]),
                            service_name=item[1],
                            vs_ip=vs_ip,
                            vs_port=vs_port,
                            vs_name=f"{service_name}-{vs_ip}-{vs_port}-vs",
                            pool_name=f"{service_name}-{vs_ip}-{vs_port}-pool",
                            pool_member=item[3],
                            pool_monitor=item[4],
                            pool_lb_method=item[5],
                            client_ssl_profile=item[6],
                            server_ssl_profile=item[7],
                            irules=item[8],
                            waf_profile=item[9],
                            f5_template=F5Template.objects.get(
                                template_name=item[10]),
                            status=status,
                            user_created=user_created,
                        )
                        model.save()
                    return JsonResponse(
                        {
                            "status": "success",
                            "message": "Create virtual server success",
                        },
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


@logged_in_or_basicauth()
def cm_f5_get_list_client_ssl_profile(request):
    if request.method == "GET":
        f5_device_ip = request.GET.get("f5_device_ip", None)
        datalist = F5ClientSSLProfile.objects.filter(
            f5_device_ip__f5_device_ip=f5_device_ip
        ).values_list("profile_name", flat=True)
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_f5_get_list_virtual_server(request):
    if request.method == "GET":
        datalist = list()
        f5_device_ip = request.GET.get("f5_device_ip", None)
        objects = F5VirtualServer.objects.filter(
            f5_device_ip__f5_device_ip=f5_device_ip
        )
        for object in objects:
            if set(object.group_permission.all()) & set(request.user.groups.all()):
                datalist.append(object.vs_name)
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_f5_get_list_server_ssl_profile(request):
    if request.method == "GET":
        f5_device_ip = request.GET.get("f5_device_ip", None)
        datalist = F5ServerSSLProfile.objects.filter(
            f5_device_ip__f5_device_ip=f5_device_ip
        ).values_list("profile_name", flat=True)
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_f5_get_list_pool_monitor(request):
    if request.method == "GET":
        f5_device_ip = request.GET.get("f5_device_ip", None)
        datalist = F5PoolMemberMonitor.objects.filter(
            f5_device_ip__f5_device_ip=f5_device_ip
        ).values_list("pool_monitor", flat=True)
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_f5_get_list_pool_lb_method(request):
    if request.method == "GET":
        datalist = F5PoolMemberMethod.objects.all().values_list(
            "pool_method", flat=True
        )
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_f5_get_list_template(request):
    if request.method == "GET":
        datalist = F5Template.objects.all().values_list("template_name", flat=True)
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_f5_get_list_waf_profile(request):
    if request.method == "GET":
        f5_device_ip = request.GET.get("f5_device_ip", None)
        datalist = F5WafProfile.objects.filter(
            f5_device_ip__f5_device_ip=f5_device_ip
        ).values_list("waf_profile", flat=True)
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_f5_get_list_irule_profile(request):
    if request.method == "GET":
        datalist = list()
        f5_device_ip = request.GET.get("f5_device_ip", None)
        objects = F5Irule.objects.filter(
            f5_device_ip__f5_device_ip=f5_device_ip
        ).values_list("irule_name", flat=True)
        for item in list(objects):
            datalist.append({"id": item, "label": item})
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_client_ssl_profile(request):
    if request.method == "POST":
        dataset = json.loads(request.body.decode("utf-8"))
        for f5_device_ip, list_client_ssl_profile in dataset.items():
            checklist = F5Device.objects.filter(
                f5_device_ip=f5_device_ip).count()
            if checklist > 0:
                for client_ssl_profile in list_client_ssl_profile:
                    f5_device_obj = F5Device.objects.get(
                        f5_device_ip=f5_device_ip)
                    F5ClientSSLProfile.objects.update_or_create(
                        f5_device_ip=f5_device_obj, profile_name=client_ssl_profile
                    )
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_server_ssl_profile(request):
    if request.method == "POST":
        dataset = json.loads(request.body.decode("utf-8"))
        for f5_device_ip, list_server_ssl_profile in dataset.items():
            checklist = F5Device.objects.filter(
                f5_device_ip=f5_device_ip).count()
            if checklist > 0:
                for server_ssl_profile in list_server_ssl_profile:
                    f5_device_obj = F5Device.objects.get(
                        f5_device_ip=f5_device_ip)
                    F5ServerSSLProfile.objects.update_or_create(
                        f5_device_ip=f5_device_obj, profile_name=server_ssl_profile
                    )
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_irule_profile(request):
    if request.method == "POST":
        dataset = json.loads(request.body.decode("utf-8"))
        for f5_device_ip, list_irule_profile in dataset.items():
            checklist = F5Device.objects.filter(
                f5_device_ip=f5_device_ip).count()
            if checklist > 0:
                for irule_profile in list_irule_profile:
                    f5_device_obj = F5Device.objects.get(
                        f5_device_ip=f5_device_ip)
                    F5Irule.objects.update_or_create(
                        f5_device_ip=f5_device_obj, irule_name=irule_profile
                    )
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_waf_profile(request):
    if request.method == "POST":
        dataset = json.loads(request.body.decode("utf-8"))
        for f5_device_ip, list_waf_profile in dataset.items():
            checklist = F5Device.objects.filter(
                f5_device_ip=f5_device_ip).count()
            if checklist > 0:
                for waf_profile in list_waf_profile:
                    f5_device_obj = F5Device.objects.get(
                        f5_device_ip=f5_device_ip)
                    F5WafProfile.objects.update_or_create(
                        f5_device_ip=f5_device_obj, waf_profile=waf_profile
                    )
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_pool_monitor(request):
    if request.method == "POST":
        dataset = json.loads(request.body.decode("utf-8"))
        for f5_device_ip, list_pool_monitor in dataset.items():
            checklist = F5Device.objects.filter(
                f5_device_ip=f5_device_ip).count()
            if checklist > 0:
                for pool_monitor in list_pool_monitor:
                    f5_device_obj = F5Device.objects.get(
                        f5_device_ip=f5_device_ip)
                    F5PoolMemberMonitor.objects.update_or_create(
                        f5_device_ip=f5_device_obj, pool_monitor=pool_monitor
                    )
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_task_virtual_server(request):
    if request.method == "POST":
        dataset = json.loads(request.body.decode("utf-8"))
        for task_id, data in dataset.items():
            checklist = F5CreateVirtualServer.objects.filter(
                id=task_id).count()
            if checklist > 0:
                status = data[0]
                message = data[1]
                F5CreateVirtualServer.objects.update_or_create(
                    id=task_id, defaults={"status": status, "message": message}
                )
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_update_task_limit_connection(request):
    if request.method == "POST":
        dataset = json.loads(request.body.decode("utf-8"))
        for task_id, data in dataset.items():
            checklist = F5LimitConnection.objects.filter(id=task_id).count()
            if checklist > 0:
                status = data[0]
                message = data[1]
                F5LimitConnection.objects.update_or_create(
                    id=task_id, defaults={"status": status, "message": message}
                )
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@csrf_exempt
@logged_in_or_basicauth()
def cm_f5_get_list_task_create_virtual_server(request):
    datalist = list()
    if request.method == "GET":
        objects = F5CreateVirtualServer.objects.filter(status="Created")
        for object in objects:
            task_id = object.id
            f5_device_ip = str(object.f5_device_ip)
            f5_template = object.f5_template
            vs_name = object.vs_name
            vs_ip = object.vs_ip
            vs_port = object.vs_port
            pool_name = object.pool_name
            pool_member = json.loads(object.pool_member)
            pool_monitor = object.pool_monitor
            pool_lb_method = object.pool_lb_method
            client_ssl_profile = object.client_ssl_profile
            server_ssl_profile = object.server_ssl_profile
            f5_temp_obj = F5Template.objects.get(template_name=f5_template)
            partition = f5_temp_obj.partition
            protocol = f5_temp_obj.protocol
            client_protocol_profile = f5_temp_obj.client_protocol_profile
            server_protocol_profile = f5_temp_obj.server_protocol_profile
            client_http_profile = f5_temp_obj.client_http_profile
            server_http_profile = f5_temp_obj.server_http_profile
            snat_name = f5_temp_obj.snat_name
            http_analytics_profile = f5_temp_obj.http_analytics_profile
            tcp_analytics_profile = f5_temp_obj.tcp_analytics_profile
            http_compression_profile = f5_temp_obj.http_compression_profile
            web_acceleration_profile = f5_temp_obj.web_acceleration_profile
            web_socket_profile = f5_temp_obj.web_socket_profile
            waf_profile = object.waf_profile
            irules = []
            if object.irules is not None:
                irules = json.loads(object.irules)
            datalist.append(
                {
                    "task_id": task_id,
                    "f5_device_ip": f5_device_ip,
                    "vs_name": vs_name,
                    "vs_ip": vs_ip,
                    "vs_port": vs_port,
                    "pool_name": pool_name,
                    "pool_member": pool_member,
                    "pool_monitor": pool_monitor,
                    "pool_lb_method": pool_lb_method,
                    "client_ssl_profile": client_ssl_profile,
                    "server_ssl_profile": server_ssl_profile,
                    "partition": partition,
                    "protocol": protocol,
                    "client_protocol_profile": client_protocol_profile,
                    "server_protocol_profile": server_protocol_profile,
                    "client_http_profile": client_http_profile,
                    "server_http_profile": server_http_profile,
                    "snat_name": snat_name,
                    "http_analytics_profile": http_analytics_profile,
                    "tcp_analytics_profile": tcp_analytics_profile,
                    "http_compression_profile": http_compression_profile,
                    "web_acceleration_profile": web_acceleration_profile,
                    "web_socket_profile": web_socket_profile,
                    "waf_profile": waf_profile,
                    "irules": irules,
                }
            )
        return JsonResponse({"status": "success", "datalist": datalist})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


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
    if request.method == "POST":
        dataset = json.loads(request.body.decode("utf-8"))
        for f5_device_ip, datalist in dataset.items():
            checklist = F5Device.objects.filter(
                f5_device_ip=f5_device_ip).count()
            if checklist > 0:
                for data in datalist:
                    vs_name = data[0]
                    vs_ip = data[1]
                    vs_port = data[2]
                    client_ssl_profile = data[3]
                    server_ssl_profile = data[4]
                    object, created = F5VirtualServer.objects.update_or_create(
                        f5_device_ip=F5Device.objects.get(
                            f5_device_ip=f5_device_ip),
                        vs_name=vs_name,
                        defaults={
                            'vs_ip': vs_ip,
                            'vs_port': vs_port,
                            'client_ssl_profile': client_ssl_profile,
                            'server_ssl_profile': server_ssl_profile
                        }
                    )
                    object.group_permission.set(
                        Group.objects.filter(name="ADMIN"))
                    object.save()
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


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

#####


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
                    error_message = check_fmc_access_rule_input(data, index)
                    if not error_message:
                        policy = data[1]
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
                        category = data[7]
                        gateway = FMCGateway.objects.filter(
                            policy__policy=policy).values_list('gateway', flat=True)
                        datalist.append(
                            [
                                policy,
                                json.dumps(list(gateway)),
                                description,
                                json.dumps(source),
                                json.dumps(destination),
                                json.dumps(protocol),
                                category,
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
                        model = FMCRule(
                            policy=FMCPolicy.objects.get(policy=item[0]),
                            gateway=item[1],
                            description=item[2],
                            source=item[3],
                            destination=item[4],
                            protocol=item[5],
                            category=item[6],
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
def cm_fmc_get_list_policy(request):
    if request.user.groups.filter(name="ADMIN").exists():
        if request.method == "GET":
            site = request.GET.get("site", None)
            datalist = []
            if site:
                datalist = FMCPolicy.objects.filter(
                    domain__site__site=site).values_list("policy", flat=True)
            return JsonResponse({"data": list(datalist)}, status=200)
        else:
            return JsonResponse({"erorr": "Method is not allowed"}, status=405)
    else:
        return JsonResponse({"erorr": "forbidden"}, status=403)


@logged_in_or_basicauth()
def cm_checkpoint_get_list_local_user(request):
    if request.user.groups.filter(name="ADMIN").exists():
        if request.method == "GET":
            datalist = []
            sites = CheckpointSite.objects.all()
            for site in sites:
                users = []
                items = CheckpointLocalUser.objects.filter(
                    Q(status="Created") | Q(status="Install-Only"), site=site)
                for item in items:
                    users.append({
                        "id": item.id,
                        "user_name": item.user_name,
                        "password": item.password,
                        "phone_number": item.phone_number,
                        "email": item.email,
                        "expiration_date": item.expiration_date
                    })

                datalist.append({
                    "smc": site.smc,
                    "smc_hostname": site.smc_hostname,
                    "users": users
                    })
            return JsonResponse({"data": datalist}, status=200)
        else:
            return JsonResponse({"erorr": "Method is not allowed"}, status=405)
    else:
        return JsonResponse({"erorr": "forbidden"}, status=403)


@csrf_exempt
@logged_in_or_basicauth()
def cm_checkpoint_update_local_user(request):
    if request.method == "POST":
        dataset = request.POST.dict()
        if dataset:
            user_id = dataset["user_id"]
            status = dataset["status"]
            message = dataset["message"]
            model = CheckpointLocalUser.objects.filter(id=user_id)
            model.update(status=status, message=message)
        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@login_required()
def cm_fmc_get_list_gateway(request):
    if request.user.groups.filter(name="ADMIN").exists():
        datalist = []
        if request.method == "GET":
            policy = request.GET.get("policy", None)
            if policy:
                try:
                    object = FMCPolicy.objects.get(policy=policy)
                    domain = object.gateway.domain.domain
                except FMCPolicy.DoesNotExist:
                    return JsonResponse({"erorr": f"Policy name: {policy} dose not exists"}, status=401)
                else:
                    objects = FMCGateway.objects.filter(
                        domain__domain=domain).values_list('gateway', flat=True)

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
def cm_fmc_update_rule_category(request):
    if request.method == "POST":
        dataset = json.loads(request.body.decode("utf-8"))
        for policy, list_rule_category in dataset.items():
            checklist = FMCPolicy.objects.filter(policy=policy).count()
            if checklist > 0:
                for rule_category in list_rule_category:
                    obj = FMCPolicy.objects.get(policy=policy)
                    FMCRuleCategory.objects.update_or_create(
                        policy=obj, category=rule_category
                    )
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error_message": "method not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_fmc_get_list_rule_category(request):
    if request.method == "GET":
        datalist = list()
        policy = request.GET.get("policy", None)
        datalist = FMCRuleCategory.objects.filter(
            policy__policy=policy
        ).values_list("category", flat=True)
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_fmc_get_list_domain(request):
    if request.method == "GET":
        datalist = list()
        site = request.GET.get("site", None)
        if site:
            datalist = FMCDomain.objects.filter(
                site__site=site).values_list("domain", flat=True)
        else:
            datalist = FMCDomain.objects.all().values_list("domain", flat=True)
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_fmc_get_list_site(request):
    if request.method == "GET":
        datalist = list()
        datalist = FMCSite.objects.all().values_list("site", flat=True)
        return JsonResponse({"status": "success", "datalist": list(datalist)})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@logged_in_or_basicauth()
def cm_fmc_get_list_rule(request):
    if request.method == "GET":
        data = dict()
        list_site = FMCSite.objects.all().values_list(
            "site", "fmc"
        )
        list_site = [list(i) for i in list_site]
        if list_site:
            for item in list_site:
                rules = FMCRule.objects.filter(
                    Q(status="Created") | Q(status="Install-Only"),
                    policy__domain__site__site=item[0],
                ).values_list(
                    "id",
                    "policy__domain__domain_id",
                    "policy__policy",
                    "gateway",
                    "description",
                    "source",
                    "destination",
                    "protocol",
                    "category",
                    "schedule",
                    "status",
                )
                rules = [list(i) for i in rules]
                if rules:
                    for obj in rules:
                        obj[3] = json.loads(obj[3])
                        obj[5] = json.loads(obj[5])
                        obj[6] = json.loads(obj[6])
                        obj[7] = json.loads(obj[7])
                site = item[0]
                data[site] = {"fmc": item[1], "rules": rules}
        return JsonResponse({"data": data}, status=200)
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)


@csrf_exempt
@logged_in_or_basicauth()
def cm_fmc_update_rule_status(request):
    if request.method == "POST":
        dataset = request.POST.dict()
        rule_id = dataset["rule_id"]
        status = dataset["status"]
        message = dataset["message"]
        model = FMCRule.objects.filter(id=rule_id)
        model.update(status=status, message=message)
        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"erorr": "Method is not allowed"}, status=405)
