from django import forms
from ipplan.models import *
from src.ipplan.func import *
from django.core.exceptions import ValidationError
from ipaddress import ip_network, IPv4Address
import re, json


def validate_xss(value):
    regex = "<([A-Za-z_{}()/]+(|=)*)+>(.*<[A-Za-z/>]+)*"
    result = re.search(regex, value)
    if result:
        raise ValidationError("The input string contains unusual characters")


class RegionForm(forms.ModelForm):
    """Form definition for IpProject."""

    region = forms.CharField(validators=[validate_xss])
    description = forms.CharField(validators=[validate_xss])

    class Meta:
        """Meta definition for IpProjectform."""

        model = Region
        fields = ("region", "description")


class LocationForm(forms.ModelForm):
    """Form definition for Location."""

    location = forms.CharField(validators=[validate_xss])
    description = forms.CharField(validators=[validate_xss])

    class Meta:
        """Meta definition for Locationform."""

        model = Location
        fields = (
            "location",
            "region",
            "description",
        )


class SubnetGroupForm(forms.ModelForm):
    """Form definition for SubnetGroup."""

    group = forms.CharField(validators=[validate_xss], label="Group name")
    description = forms.CharField(validators=[validate_xss])

    class Meta:
        """Meta definition for Locationform."""

        model = SubnetGroup
        fields = (
            "group",
            "group_subnet",
            "location",
            "description",
        )


class SubnetForm(forms.ModelForm):
    """Form definition for Subnet."""

    name = forms.CharField(validators=[validate_xss])
    description = forms.CharField(validators=[validate_xss])

    class Meta:
        """Meta definition for Subnetform."""

        model = Subnet
        fields = ("subnet", "name", "group", "vlan", "description")

    def clean(self):
        subnet = self.cleaned_data.get("subnet")
        group_obj = self.cleaned_data.get("group")
        group_subnet = group_obj.group_subnet
        if is_subnet(subnet) is False:
            raise ValidationError("Subnet is invalid")
        elif ip_network(subnet).subnet_of(ip_network(group_subnet)) is False:
            raise ValidationError("Subnet is not in group subnet")


class SubnetUpdateForm(forms.ModelForm):
    """Form definition for Subnet."""

    name = forms.CharField(validators=[validate_xss])
    description = forms.CharField(validators=[validate_xss])

    class Meta:
        """Meta definition for Subnetform."""

        model = Subnet
        fields = ("name", "group", "vlan", "description")


class RequestIpAddressForm(forms.Form):
    """RequestIpAddressForm definition."""

    subnet = forms.ModelChoiceField(queryset=Subnet.objects.all())
    ip = forms.CharField(validators=[validate_xss], widget=forms.SelectMultiple)
    description = forms.CharField(max_length=200, validators=[validate_xss])

    def clean_subnet(self):
        subnet = self.cleaned_data.get("subnet")
        is_subnet_exists = Subnet.objects.filter(subnet=subnet).exists()
        if not is_subnet(subnet):
            raise ValidationError("Subnet is not validated")
        elif not is_subnet_exists:
            raise ValidationError("This subnet is not in database")
        return subnet


class IpAddressModelForm(forms.ModelForm):
    """Form definition for IpAddressModel."""

    class Meta:
        """Meta definition for IpAddressModelform."""

        model = IpAddressModel
        fields = (
            "ip",
            "subnet",
            "description",
        )


class IpAddressModelUpdatelForm(forms.ModelForm):
    """Form definition for IpAddressModelUpdatelForm."""

    description = forms.CharField(validators=[validate_xss])

    class Meta:
        """Meta definition for IpAddressModelUpdatelForm."""

        model = IpAddressModel
        fields = ("ip", "description", "inused")


class IPPlanExportForm(forms.Form):
    CHOICES = (("1", "List subnets"),)
    database_table = forms.ChoiceField(
        label="Select database to export", choices=CHOICES, required=False
    )
