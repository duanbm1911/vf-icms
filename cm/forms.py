from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import modelformset_factory
from django import forms
from cm.models import *


CHECKPOINT_ACCESS_RULE_STATUS = (
    ("Created", "Created"),
    ("Success", "Success"),
    ("Install-Only", "Install-Only"),
)

CHECKPOINT_LOCAL_USER_STATUS = (
    ("Created", "Created"),
    ("Success", "Success")
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

EMAIL_ALERT_TEMPLATE = (
    ("UserExpiring", "UserExpiring"),
    ("UserLocked", "UserLocked"),
    ("UserActivity", "UserActivity")
)

class CheckpointPolicyForm(forms.ModelForm):
    class Meta:

        model = CheckpointPolicy
        fields = ["site", "policy", "layer"]


class CheckpointSiteForm(forms.ModelForm):
    class Meta:

        model = CheckpointSite
        fields = ["site", "smc", "smc_hostname"]


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

class CheckpointLocalUserTemplateForm(forms.ModelForm):

    class Meta:
        model = CheckpointLocalUserTemplate
        fields = [
            "name",
            "site",
            "default_group",
            "radius_group_server",
            "skip_send_alert_email"
        ]
    

class CheckpointEmailAlertTemplateForm(forms.ModelForm):
    template_name = forms.ChoiceField(choices=EMAIL_ALERT_TEMPLATE)
    email_body = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'code-editor', 
            'class': 'form-control'
        }),
        label="Email Body (Code)"
    )

    class Meta:
        model = CheckpointEmailAlertTemplate
        fields = ['template_name', 'email_title', 'email_body']
    

class CheckpointLocalUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    expiration_date = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}), required=True)
    status = forms.ChoiceField(choices=CHECKPOINT_LOCAL_USER_STATUS)
    
    class Meta:

        model = CheckpointLocalUser
        fields = [
            "template", 
            "user_name", 
            "is_partner",
            "password", 
            "email", 
            "phone_number", 
            "expiration_date", 
            "user_group", 
            "custom_group",
            "status"]
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        try:
            if email is not None:
                validate_email(email)
            else:
                pass
        except ValidationError:
            raise forms.ValidationError("Invalid email. Please enter correct format.")
            
        return email
    
    def clean_smc(self):
        smc = self.cleaned_data.get('smc')
        
        if not smc:
            raise forms.ValidationError("Invalid SMC. Please select a SMC")
            
        return smc
    
class CheckpointLocalUserBulkForm(forms.Form):
    user_names = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter user names (one per line). Existing users will be updated.",
        label="User name"
    )
    
    template = forms.ModelChoiceField(
        queryset=CheckpointLocalUserTemplate.objects.all(),
        required=False
    )
    is_partner = forms.BooleanField(required=False, initial=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    email = forms.EmailField(required=False)
    phone_number = forms.IntegerField(required=False)
    expiration_date = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}),
        required=False
    )
    user_group = forms.ModelMultipleChoiceField(
        queryset=CheckpointLocalUserGroup.objects.all(),
        required=False
    )
    custom_group = forms.CharField(max_length=200, required=False)
    status = forms.ChoiceField(
        choices=CHECKPOINT_LOCAL_USER_STATUS, 
        required=False
    )

class FMCPolicyForm(forms.ModelForm):
    class Meta:

        model = FMCPolicy
        fields = ["domain", "policy"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        domains = FMCDomain.objects.select_related('site')
        
        self.fields['domain'] = forms.ModelChoiceField(
            queryset=domains,
            label="Domain",
            widget=forms.Select(attrs={'class': 'form-control'}),
        )
        
        self.fields['domain'].label_from_instance = lambda obj: f"{obj.domain} ({obj.site})"


class FMCSiteForm(forms.ModelForm):
    class Meta:

        model = FMCSite
        fields = ["site", "fmc"]


class FMCGatewayForm(forms.ModelForm):
    class Meta:

        model = FMCGateway
        fields = ["policy", "gateway"]


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
