from typing import Collection
from django.db import models
from django.core.exceptions import ValidationError


# Create your models here.


class DeviceProvince(models.Model):
    device_province = models.CharField(max_length=200, unique=True, verbose_name="P&L")
    description = models.CharField(max_length=200)
    creation_time = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100)

    def __str__(self):
        return self.device_province


class DeviceType(models.Model):
    device_type = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200)
    creation_time = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100)

    def __str__(self):
        return self.device_type


class DeviceCategory(models.Model):
    device_category = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200)
    creation_time = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100)

    def __str__(self):
        return self.device_category


class DeviceVendor(models.Model):
    device_vendor = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200)
    creation_time = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100)

    def __str__(self):
        return self.device_vendor


class DeviceOS(models.Model):
    device_os = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200)
    creation_time = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100)

    def __str__(self):
        return self.device_os


class DeviceBranch(models.Model):
    device_branch = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200)
    creation_time = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100)

    def __str__(self):
        return self.device_branch


class DeviceGroup(models.Model):
    device_group = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200)
    creation_time = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100)

    def __str__(self):
        return str(self.device_group)


class Device(models.Model):
    device_name = models.CharField(max_length=200)
    device_ip = models.GenericIPAddressField(unique=True)
    device_province = models.ForeignKey(
        'DeviceProvince', on_delete=models.PROTECT)
    device_branch = models.ForeignKey('DeviceBranch', on_delete=models.PROTECT)
    device_type = models.ForeignKey('DeviceType', on_delete=models.PROTECT)
    device_category = models.ForeignKey(
        'DeviceCategory', on_delete=models.PROTECT)
    device_vendor = models.ForeignKey('DeviceVendor', on_delete=models.PROTECT)
    device_os = models.ForeignKey('DeviceOS', on_delete=models.PROTECT)
    device_group = models.ForeignKey(
        'DeviceGroup', on_delete=models.PROTECT, null=True, blank=True)
    device_firmware = models.CharField(max_length=200, blank=True)
    device_status = models.CharField(max_length=200, blank=True)
    device_stack = models.BooleanField(default=False)
    device_description = models.CharField(max_length=200, blank=True)
    device_creation_time = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.device_ip


class DeviceManagement(models.Model):
    """Model definition for DeviceManagement."""

    device_ip = models.ForeignKey('Device', on_delete=models.CASCADE)
    device_serial_number = models.CharField(
        max_length=100, blank=True, unique=True)
    start_ma_date = models.DateField(blank=True, null=True)
    end_ma_date = models.DateField(blank=True, null=True)
    start_license_date = models.DateField(blank=True, null=True)
    end_license_date = models.DateField(blank=True, null=True)
    end_sw_support_date = models.DateField(blank=True, null=True)
    end_hw_support_date = models.DateField(blank=True, null=True)
    start_used_date = models.DateField(blank=True, null=True)
    user_created = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        """Unicode representation of DeviceManagement."""
        return str(self.device_serial_number)


class DeviceRackLayout(models.Model):
    """Model definition for DeviceRackLayout."""

    device_ip = models.ForeignKey('Device', on_delete=models.CASCADE)
    device_serial_number = models.OneToOneField(
        'DeviceManagement', on_delete=models.CASCADE)
    device_rack_name = models.CharField(max_length=200, blank=True)
    device_rack_unit = models.CharField(max_length=200, blank=True)
    user_created = models.CharField(max_length=100, blank=True)

    def __str__(self):
        """Unicode representation of DeviceRackLayout."""
        return str(self.device_ip)


class DeviceFirmware(models.Model):
    """Model definition for DeviceFirmware."""

    device_type = models.ForeignKey("DeviceType", on_delete=models.CASCADE)
    firmware = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)
    creation_time = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100, blank=True)

    def __str__(self):
        """Unicode representation of DeviceFirmware."""
        return str(self.firmware)
