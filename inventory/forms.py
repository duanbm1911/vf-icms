from django import forms
from inventory.models import *
from django.core.exceptions import ValidationError
import re


def is_xss_validate(value):
    regex = "<([A-Za-z0-9_{}()/]+(\s|=)*)+>(.*<[A-Za-z/>]+)*"
    result = re.search(regex, value)
    if result:
        raise ValidationError("The input string contains unusual characters")


class DeviceForm(forms.ModelForm):
    device_name = forms.CharField(validators=[is_xss_validate])
    device_description = forms.CharField(validators=[is_xss_validate], required=False)

    class Meta:

        model = Device
        fields = [  
            'device_name', 
            'device_ip', 
            'device_province', 
            'device_branch',
            'device_type',
            'device_category', 
            'device_vendor',
            'device_os',
            'device_group',
            'device_stack',
            'device_description'
        ]


class DeviceProvinceForm(forms.ModelForm):
    device_province = forms.CharField(validators=[is_xss_validate])
    description = forms.CharField(validators=[is_xss_validate])

    class Meta:

        model = DeviceProvince
        fields = ["device_province", "description"]


class DeviceOSForm(forms.ModelForm):
    device_os = forms.CharField(validators=[is_xss_validate])
    description = forms.CharField(validators=[is_xss_validate])

    class Meta:

        model = DeviceOS
        fields = ["device_os", "description"]


class DeviceTypeForm(forms.ModelForm):
    device_type = forms.CharField(validators=[is_xss_validate])
    description = forms.CharField(validators=[is_xss_validate])

    class Meta:

        model = DeviceType
        fields = ["device_type", "description"]


class DeviceCategoryForm(forms.ModelForm):
    device_category = forms.CharField(validators=[is_xss_validate])
    description = forms.CharField(validators=[is_xss_validate])

    class Meta:

        model = DeviceCategory
        fields = ["device_category", "description"]


class DeviceVendorForm(forms.ModelForm):
    device_vendor = forms.CharField(validators=[is_xss_validate])
    description = forms.CharField(validators=[is_xss_validate])

    class Meta:

        model = DeviceVendor
        fields = ["device_vendor", "description"]


class DeviceBranchForm(forms.ModelForm):
    device_branch = forms.CharField(validators=[is_xss_validate])
    description = forms.CharField(validators=[is_xss_validate])

    class Meta:

        model = DeviceBranch
        fields = ["device_branch", "description"]


class DeviceGroupForm(forms.ModelForm):
    device_group = forms.CharField(validators=[is_xss_validate])
    description = forms.CharField(validators=[is_xss_validate])

    class Meta:

        model = DeviceGroup
        fields = ["device_group", "description"]


class CreateDeviceForm(forms.Form):
    upload_file = forms.FileField()


class DeviceManagementForm(forms.ModelForm):
    start_ma_date = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}), required=False
    )
    end_ma_date = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}), required=False
    )
    start_license_date = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}), required=False
    )
    end_license_date = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}), required=False
    )
    end_sw_support_date = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}), required=False
    )
    end_hw_support_date = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}), required=False
    )
    start_used_date = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}), required=False
    )
    device_serial_number = forms.CharField(validators=[is_xss_validate])

    class Meta:
        model = DeviceManagement
        fields = [
            "device_ip",
            "device_serial_number",
            "start_ma_date",
            "end_ma_date",
            "start_license_date",
            "end_license_date",
            "end_sw_support_date",
            "end_hw_support_date",
            "start_used_date",
        ]


class DeviceRackLayoutForm(forms.ModelForm):
    class Meta:
        model = DeviceRackLayout
        fields = [
            'device_ip',
            'device_serial_number',
            'device_rack_name',
            'device_rack_unit'
        ]

        
class DeviceExportForm(forms.Form):
    CHOICES = (
        ('1', 'Device'),
        ('2', 'Device management'),
        ('3', 'Device rack layout'),
        ('4', 'Device incorrect firmware'),
        ('5', 'Device expired license (6 months)'))
    database_table = forms.ChoiceField(label=False, choices=CHOICES, required=False)
    
class DeviceFirmwareForm(forms.ModelForm):
    class Meta:
        model = DeviceFirmware
        fields = ["device_type", "firmware", "description"]


class DeviceSearchForm(forms.Form):
    device_branch = forms.ModelMultipleChoiceField(
        queryset=DeviceBranch.objects.all(), 
        required=False, 
        widget=forms.SelectMultiple, 
        label="Device Branch"
    )
    device_type = forms.ModelMultipleChoiceField(
        queryset=DeviceType.objects.all(), 
        required=False, 
        widget=forms.SelectMultiple, 
        label="Device Type"
    )
    device_category = forms.ModelMultipleChoiceField(
        queryset=DeviceCategory.objects.all(), 
        required=False, 
        widget=forms.SelectMultiple, 
        label="Device Category"
    )
    device_vendor = forms.ModelMultipleChoiceField(
        queryset=DeviceVendor.objects.all(), 
        required=False, 
        widget=forms.SelectMultiple, 
        label="Device Vendor"
    )
    device_os = forms.ModelMultipleChoiceField(
        queryset=DeviceOS.objects.all(), 
        required=False, 
        widget=forms.SelectMultiple, 
        label="Device OS"
    )
    device_group = forms.ModelMultipleChoiceField(
        queryset=DeviceGroup.objects.all(), 
        required=False, 
        widget=forms.SelectMultiple, 
        label="Device Group"
    )
    
class DeviceManagementSearchForm(forms.Form):
    device_branch = forms.ModelMultipleChoiceField(
        queryset=DeviceBranch.objects.all(), 
        required=False, 
        widget=forms.SelectMultiple, 
        label="Device Branch"
    )
    device_ip = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        widget=forms.Select,
        label="Device IP"
    )