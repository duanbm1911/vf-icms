from django import forms
from cm.models import *


CHECKPOINT_ACCESS_RULE_STATUS = (
    ("Created", "Created"),
    ("Success", "Success"),
    ("Install-Only", "Install-Only"),
)

FMC_ACCESS_RULE_STATUS = (
    ("Created", "Created"),
    ("Success", "Success"),
    ("Install-Only", "Install-Only"),
)

F5_VIRTUAL_SERVER_STATUS = (
    ("Created", "Created"),
    ("Success", "Success"),
    ("Failed", "Failed"),
)


class CheckpointPolicyForm(forms.ModelForm):
    class Meta:

        model = CheckpointPolicy
        fields = ["policy", "layer", "site"]


class CheckpointSiteForm(forms.ModelForm):
    class Meta:

        model = CheckpointSite
        fields = ["site", "smc"]


class CheckpointGatewayForm(forms.ModelForm):
    class Meta:

        model = CheckpointGateway
        fields = ["site", "policy", "gateway"]


class CheckpointRuleForm(forms.ModelForm):

    status = forms.ChoiceField(choices=CHECKPOINT_ACCESS_RULE_STATUS)

    class Meta:
        model = CheckpointRule
        fields = [
            "policy",
            "description",
            "source",
            "destination",
            "protocol",
            "section",
            "schedule",
            "status",
        ]


class FMCPolicyForm(forms.ModelForm):
    class Meta:

        model = FMCPolicy
        fields = ["policy", "gateway"]


class FMCSiteForm(forms.ModelForm):
    class Meta:

        model = FMCSite
        fields = ["site", "fmc"]


class FMCGatewayForm(forms.ModelForm):
    class Meta:

        model = FMCGateway
        fields = ["domain", "gateway"]


class FMCDomainForm(forms.ModelForm):
    class Meta:

        model = FMCDomain
        fields = ["site", "domain", "domain_id"]


class FMCRuleForm(forms.ModelForm):

    status = forms.ChoiceField(choices=FMC_ACCESS_RULE_STATUS)

    class Meta:
        model = FMCRule
        fields = [
            "policy",
            "description",
            "source",
            "destination",
            "protocol",
            "category",
            "schedule",
            "status",
        ]


class F5DeviceForm(forms.ModelForm):
    class Meta:
        model = F5Device
        fields = [
            "f5_device_ip",
            "f5_device_name",
        ]


class F5VirtualServerPermissionForm(forms.ModelForm):
    class Meta:
        model = F5VirtualServer
        fields = [
            "f5_device_ip",
            "vs_ip",
            "vs_port",
            "vs_name",
            "group_permission"
        ]


class F5VirtualServerForm(forms.ModelForm):
    class Meta:
        model = F5VirtualServer
        fields = [
            "f5_device_ip",
            "vs_ip",
            "vs_port",
            "vs_name",
            "service_dns_name",
            "client_ssl_profile",
            "server_ssl_profile",
            "service_owner",
            "center_head"
        ]


class F5CreateVirtualServerForm(forms.ModelForm):

    status = forms.ChoiceField(choices=F5_VIRTUAL_SERVER_STATUS)

    class Meta:
        model = F5CreateVirtualServer
        fields = [
            "f5_device_ip",
            "f5_template",
            "service_name",
            "vs_name",
            "vs_ip",
            "vs_port",
            "pool_member",
            "pool_monitor",
            "pool_lb_method",
            "client_ssl_profile",
            "server_ssl_profile",
            "irules",
            "waf_profile",
            "status",
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)  # Lấy request từ kwargs
        super(F5CreateVirtualServerForm, self).__init__(*args, **kwargs)


class F5LimitConnectionForm(forms.ModelForm):

    vs_name = forms.CharField(widget=forms.Select)

    class Meta:
        model = F5LimitConnection
        fields = ["f5_device_ip", "vs_name", "connection_number"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)  # Lấy request từ kwargs
        super(F5LimitConnectionForm, self).__init__(*args, **kwargs)

    def clean_vs_name(self):
        vs_name = self.cleaned_data["vs_name"]
        f5_device_ip = self.cleaned_data["f5_device_ip"]
        try:
            object = F5VirtualServer.objects.get(
                f5_device_ip__f5_device_ip=f5_device_ip, vs_name=vs_name
            )
        except:
            raise forms.ValidationError(
                f"Virtual server name: {vs_name} does not exists"
            )
        else:
            if set(object.group_permission.all()) & set(self.request.user.groups.all()):
                return vs_name
            else:
                raise forms.ValidationError(
                    f"You do not have permission to configure this virtual server"
                )


class F5LimitConnectionFormUpdate(forms.ModelForm):

    status = forms.ChoiceField(choices=F5_VIRTUAL_SERVER_STATUS)

    class Meta:
        model = F5LimitConnection
        fields = ["f5_device_ip", "vs_name", "connection_number", "status"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)  # Lấy request từ kwargs
        super(F5LimitConnectionFormUpdate, self).__init__(*args, **kwargs)

    def clean_vs_name(self):
        vs_name = self.cleaned_data["vs_name"]
        f5_device_ip = self.cleaned_data["f5_device_ip"]
        try:
            object = F5VirtualServer.objects.get(
                f5_device_ip__f5_device_ip=f5_device_ip, vs_name=vs_name
            )
        except:
            raise forms.ValidationError(
                f"Virtual server name: {vs_name} does not exists"
            )
        else:
            if set(object.group_permission.all()) & set(self.request.user.groups.all()):
                return vs_name
            else:
                raise forms.ValidationError(
                    f"You do not have permission to configure this virtual server"
                )


class F5TemplateForm(forms.ModelForm):
    class Meta:
        model = F5Template
        fields = [
            "template_name",
            "partition",
            "protocol",
            "client_protocol_profile",
            "server_protocol_profile",
            "client_http_profile",
            "server_http_profile",
            "snat_name",
            "http_analytics_profile",
            "tcp_analytics_profile",
            "web_socket_profile",
            "http_compression_profile",
            "web_acceleration_profile",
        ]


class F5ExportForm(forms.Form):
    CHOICES = (
        ('1', 'Virtual server'),)
    database_table = forms.ChoiceField(
        label=False, choices=CHOICES, required=False)
