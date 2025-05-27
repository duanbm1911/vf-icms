from django.contrib import admin
from cm.models import *
from inventory.models import *
from ipplan.models import *
from django.contrib.auth.models import *
from accounts.models import *

# Register your models here.

from django.contrib import admin


class MyAdminSite(admin.AdminSite):
    site_header = "ICMS ADMINISTRATOR"


admin_site = MyAdminSite(name="ICMS_ADMIN")
admin_site.register(DeviceProvince)
admin_site.register(DeviceType)
admin_site.register(DeviceCategory)
admin_site.register(DeviceVendor)
admin_site.register(DeviceOS)
admin_site.register(Device)
admin_site.register(DeviceManagement)
admin_site.register(DeviceRackLayout)
admin_site.register(DeviceFirmware)
admin_site.register(DeviceBranch)
admin_site.register(DeviceGroup)
admin_site.register(CheckpointRule)
admin_site.register(CheckpointSite)
admin_site.register(CheckpointRuleSection)
admin_site.register(CheckpointPolicy)
admin_site.register(CheckpointGateway)
admin_site.register(CheckpointLocalUserTemplate)
admin_site.register(FMCRule)
admin_site.register(FMCSite)
admin_site.register(FMCRuleCategory)
admin_site.register(FMCPolicy)
admin_site.register(FMCGateway)
admin_site.register(FMCDomain)
admin_site.register(Region)
admin_site.register(Location)
admin_site.register(Subnet)
admin_site.register(SubnetGroup)
admin_site.register(IpAddressModel)
admin_site.register(User)
admin_site.register(Group)
admin_site.register(UserOTP)
admin_site.register(ClientLoginFailedSession)
admin_site.register(F5CreateVirtualServer)
admin_site.register(F5Device)
admin_site.register(F5ClientSSLProfile)
admin_site.register(F5ServerSSLProfile)
admin_site.register(F5Template)
admin_site.register(F5Irule)
admin_site.register(F5WafProfile)
admin_site.register(F5PoolMemberMethod)
admin_site.register(F5PoolMemberMonitor)
admin_site.register(F5VirtualServer)
admin_site.register(F5LimitConnection)