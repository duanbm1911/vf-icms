from django.db import models

# Create your models here.


class Region(models.Model):
    """Model definition for Region."""

    region = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)
    time_created = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100)

    def __str__(self):
        """Unicode representation of Region."""
        return self.region


class Location(models.Model):
    """Model definition for Location."""

    location = models.CharField(max_length=100, unique=True)
    region = models.ForeignKey("Region", on_delete=models.CASCADE)
    description = models.CharField(max_length=200, blank=True)
    time_created = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100)

    def __str__(self):
        """Unicode representation of Location."""
        return self.location


class SubnetGroup(models.Model):
    group = models.CharField(max_length=200, unique=True)
    location = models.ForeignKey("Location", on_delete=models.CASCADE)
    group_subnet = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)
    time_created = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100)

    def __str__(self):
        """Unicode representation of Subnet."""
        return self.group


class Subnet(models.Model):
    """Model definition for Subnet."""

    subnet = models.CharField(max_length=100, unique=True)
    group = models.ForeignKey("SubnetGroup", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    vlan = models.IntegerField(blank=True)
    description = models.CharField(max_length=200, blank=True)
    time_created = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100)

    def __str__(self):
        """Unicode representation of Subnet."""
        return self.subnet


class IpAddressModel(models.Model):
    """Model definition for IpModel."""

    ip = models.GenericIPAddressField(unique=True)
    subnet = models.ForeignKey("Subnet", on_delete=models.CASCADE)
    status = models.CharField(max_length=200, blank=True)
    inused = models.BooleanField(default=False)
    description = models.CharField(max_length=200, blank=True)
    time_created = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=100)

    def __str__(self):
        """Unicode representation of IpModel."""
        return self.ip
