from django.db import models
from django.contrib.auth.models import Group

# Create your models here.


class CheckpointPolicy(models.Model):
    policy = models.CharField(max_length=200, unique=True)
    layer = models.CharField(max_length=100, blank=True, null=True)
    site = models.ForeignKey("CheckpointSite", on_delete=models.CASCADE)

    def __str__(self):
        return self.policy


class CheckpointSite(models.Model):
    site = models.CharField(max_length=100, unique=True)
    smc = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.site


class CheckpointRuleSection(models.Model):
    policy = models.ForeignKey("CheckpointPolicy", on_delete=models.CASCADE)
    section = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.section
    
class CheckpointGateway(models.Model):
    site = models.ForeignKey('CheckpointSite', on_delete=models.CASCADE)
    policy = models.ForeignKey('CheckpointPolicy', on_delete=models.CASCADE, null=True, blank=True)
    gateway = models.CharField(max_length=500, unique=True)
    
    def __str__(self):
        return self.gateway


class CheckpointRule(models.Model):
    policy = models.ForeignKey("CheckpointPolicy", on_delete=models.CASCADE)
    gateway = models.CharField(max_length=500)
    description = models.CharField(max_length=1000)
    source = models.CharField(max_length=1000)
    destination = models.CharField(max_length=1000)
    protocol = models.CharField(max_length=1000)
    schedule = models.CharField(max_length=1000, blank=True)
    section = models.CharField(max_length=100, blank=True)
    user_created = models.CharField(max_length=200)
    time_created = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=200, default='Created')
    message = models.CharField(max_length=3000, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class FMCSite(models.Model):
    site = models.CharField(max_length=100, unique=True)
    fmc = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.site


class FMCDomain(models.Model):
    site = models.ForeignKey('FMCSite', on_delete=models.CASCADE)
    domain = models.CharField(max_length=500)
    domain_id = models.CharField(max_length=500)
    
    def __str__(self):
        return self.domain
    
class FMCGateway(models.Model):
    domain = models.ForeignKey('FMCDomain', on_delete=models.CASCADE)
    gateway = models.CharField(max_length=500, unique=True)
    
    def __str__(self):
        return self.gateway

class FMCPolicy(models.Model):
    policy = models.CharField(max_length=200, unique=True)
    gateway = models.ForeignKey("FMCGateway", on_delete=models.CASCADE)

    def __str__(self):
        return self.policy

class FMCRuleCategory(models.Model):
    policy = models.ForeignKey("FMCPolicy", on_delete=models.CASCADE)
    category = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.category

class FMCRule(models.Model):
    policy = models.ForeignKey("FMCPolicy", on_delete=models.CASCADE)
    gateway = models.CharField(max_length=500)
    description = models.CharField(max_length=1000)
    source = models.CharField(max_length=1000)
    destination = models.CharField(max_length=1000)
    protocol = models.CharField(max_length=1000)
    schedule = models.CharField(max_length=1000, blank=True)
    category = models.CharField(max_length=100, blank=True)
    user_created = models.CharField(max_length=200)
    time_created = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=200, default='Created')
    message = models.CharField(max_length=3000, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class F5Device(models.Model):
    f5_device_ip = models.CharField(max_length=200)
    f5_device_name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.f5_device_ip)


class F5CreateVirtualServer(models.Model):
    f5_device_ip = models.ForeignKey("F5Device", on_delete=models.PROTECT)
    f5_template = models.ForeignKey("F5Template", on_delete=models.PROTECT)
    service_name = models.CharField(max_length=200)
    vs_name = models.CharField(max_length=200)
    vs_ip = models.GenericIPAddressField()
    vs_port = models.IntegerField()
    pool_name = models.CharField(max_length=200)
    pool_member = models.CharField(max_length=1000)
    pool_monitor = models.CharField(max_length=200)
    pool_lb_method = models.CharField(max_length=200)
    client_ssl_profile = models.CharField(max_length=200, blank=True)
    server_ssl_profile = models.CharField(max_length=200, blank=True)
    irules = models.CharField(max_length=200, blank=True)
    waf_profile = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=200, blank=True)
    message = models.CharField(max_length=1000, blank=True)
    task_name = models.CharField(max_length=200, default="create-virtual-server")
    tag = models.CharField(max_length=200, default="badge-warning")
    time_created = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=200)

    def __str__(self):
        return str(self.service_name)


class F5VirtualServer(models.Model):
    f5_device_ip = models.ForeignKey("F5Device", on_delete=models.CASCADE)
    vs_ip = models.GenericIPAddressField()
    vs_port = models.IntegerField()
    vs_name = models.CharField(max_length=200)
    service_dns_name = models.CharField(max_length=200, blank=True, null=True)
    client_ssl_profile = models.CharField(max_length=200, blank=True, null=True)
    server_ssl_profile = models.CharField(max_length=200, blank=True, null=True)
    service_owner = models.CharField(max_length=200, blank=True, null=True)
    center_head = models.CharField(max_length=200, blank=True, null=True)
    group_permission = models.ManyToManyField(Group)

    def __str__(self):
        return str(self.vs_name)


class F5LimitConnection(models.Model):
    f5_device_ip = models.ForeignKey("F5Device", on_delete=models.CASCADE)
    vs_name = models.CharField(max_length=200)
    connection_number = models.IntegerField()
    status = models.CharField(max_length=200, default="Created")
    message = models.CharField(max_length=1000, blank=True)
    task_name = models.CharField(max_length=200, default="create-limit-connection")
    tag = models.CharField(max_length=200, default="badge-danger")
    time_created = models.DateTimeField(auto_now=True)
    user_created = models.CharField(max_length=200)

    def __str__(self):
        return str(self.vs_name)


class F5ClientSSLProfile(models.Model):
    f5_device_ip = models.ForeignKey("F5Device", on_delete=models.PROTECT)
    profile_name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.profile_name)


class F5ServerSSLProfile(models.Model):
    f5_device_ip = models.ForeignKey("F5Device", on_delete=models.PROTECT)
    profile_name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.profile_name)


class F5Irule(models.Model):
    f5_device_ip = models.ForeignKey("F5Device", on_delete=models.PROTECT)
    irule_name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.irule_name)


class F5WafProfile(models.Model):
    f5_device_ip = models.ForeignKey("F5Device", on_delete=models.PROTECT)
    waf_profile = models.CharField(max_length=200)

    def __str__(self):
        return str(self.waf_profile)


class F5PoolMemberMonitor(models.Model):
    f5_device_ip = models.ForeignKey("F5Device", on_delete=models.PROTECT)
    pool_monitor = models.CharField(max_length=200)

    def __str__(self):
        return str(self.pool_monitor)


class F5PoolMemberMethod(models.Model):
    pool_method = models.CharField(max_length=200)

    def __str__(self):
        return str(self.pool_method)


class F5Template(models.Model):
    template_name = models.CharField(max_length=200, unique=True)
    partition = models.CharField(max_length=200, blank=True)
    protocol = models.CharField(max_length=200, blank=True)
    client_protocol_profile = models.CharField(max_length=200, blank=True)
    server_protocol_profile = models.CharField(max_length=200, blank=True)
    client_http_profile = models.CharField(max_length=200, blank=True)
    server_http_profile = models.CharField(max_length=200, blank=True)
    snat_name = models.CharField(max_length=200, blank=True)
    http_analytics_profile = models.CharField(max_length=200, blank=True)
    tcp_analytics_profile = models.CharField(max_length=200, blank=True)
    web_socket_profile = models.CharField(max_length=200, blank=True)
    http_compression_profile = models.CharField(max_length=200, blank=True)
    web_acceleration_profile = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return str(self.template_name)
