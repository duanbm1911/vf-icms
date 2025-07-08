from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.views.generic import FormView
from django.db.utils import IntegrityError
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib import messages
from cm.models import *
from cm.forms import *
from django.db.models import Q

from django.db import transaction
import io, csv, openpyxl

# Create your views here.



class CheckpointRuleView(TemplateView):
    template_name = "checkpoint/access_rule/create.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)


class CheckpointPolicyCreateView(CreateView):
    model = CheckpointPolicy
    form_class = CheckpointPolicyForm
    template_name = "checkpoint/policy/create.html"
    success_url = reverse_lazy("checkpoint_list_policy")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Create success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context


class CheckpointPolicyListView(ListView):
    model = CheckpointPolicy
    context_object_name = "objects"
    template_name = "checkpoint/policy/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CheckpointPolicyUpdateView(UpdateView):
    model = CheckpointPolicy
    form_class = CheckpointPolicyForm
    template_name = "checkpoint/policy/update.html"
    success_url = reverse_lazy("checkpoint_list_policy")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class CheckpointPolicyDeleteView(DeleteView):
    model = CheckpointPolicy
    template_name = "checkpoint/policy/list.html"
    success_url = reverse_lazy("checkpoint_list_policy")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)


class CheckpointSiteCreateView(CreateView):
    model = CheckpointSite
    form_class = CheckpointSiteForm
    template_name = "checkpoint/site/create.html"
    success_url = reverse_lazy("checkpoint_list_site")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Create success")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context


class CheckpointSiteListView(ListView):
    model = CheckpointSite
    context_object_name = "objects"
    template_name = "checkpoint/site/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CheckpointSiteUpdateView(UpdateView):
    model = CheckpointSite
    form_class = CheckpointSiteForm
    template_name = "checkpoint/site/update.html"
    success_url = reverse_lazy("checkpoint_list_site")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context
    

class CheckpointSiteDeleteView(DeleteView):
    model = CheckpointSite
    template_name = "checkpoint/site/list.html"
    success_url = reverse_lazy("checkpoint_list_site")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)

# gateway
class CheckpointGatewayCreateView(CreateView):
    model = CheckpointGateway
    form_class = CheckpointGatewayForm
    template_name = "checkpoint/gateway/create.html"
    success_url = reverse_lazy("checkpoint_list_gateway")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Create success")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context


class CheckpointGatewayListView(ListView):
    model = CheckpointGateway
    context_object_name = "objects"
    template_name = "checkpoint/gateway/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CheckpointGatewayUpdateView(UpdateView):
    model = CheckpointGateway
    form_class = CheckpointGatewayForm
    template_name = "checkpoint/gateway/update.html"
    success_url = reverse_lazy("checkpoint_list_gateway")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class CheckpointGatewayDeleteView(DeleteView):
    model = CheckpointGateway
    template_name = "checkpoint/gateway/list.html"
    success_url = reverse_lazy("checkpoint_list_gateway")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)
# endgateway


class CheckpointRuleListView(ListView):
    model = CheckpointRule
    context_object_name = "objects"
    template_name = "checkpoint/access_rule/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            "list_rule_created": CheckpointRule.objects.filter(Q(status="Created") | Q(status="Install-Only")),
            "list_rule_process": CheckpointRule.objects.filter(status="Processing"),
            "list_rule_success": CheckpointRule.objects.filter(status="Success").order_by("-id")[:500],
            "list_rule_failed": CheckpointRule.objects.filter(status="Failed"),
        }
        return context


class CheckpointRuleDeleteView(DeleteView):
    model = CheckpointRule
    template_name = "checkpoint/site/list.html"
    success_url = reverse_lazy("checkpoint_list_task_access_rule")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)


class CheckpointRuleDetailView(DetailView):
    model = CheckpointRule
    template_name = "checkpoint/access_rule/detail.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CheckpointRuleUpdateView(UpdateView):
    model = CheckpointRule
    form_class = CheckpointRuleForm
    template_name = "checkpoint/access_rule/update.html"
    success_url = reverse_lazy("checkpoint_list_task_access_rule")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class F5TaskListView(ListView):
    model = F5CreateVirtualServer
    template_name = "f5/tasks/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        list_task = list()
        list_task_01 = F5CreateVirtualServer.objects.all()
        list_task_02 = F5LimitConnection.objects.all()
        for item in list_task_01:
            list_task.append(
                {
                    "id": item.id,
                    "f5_device_ip": item.f5_device_ip.f5_device_ip,
                    "vs_name": item.vs_name,
                    "task_name": item.task_name,
                    "tag": item.tag,
                    "status": item.status,
                    "message": item.message,
                    "time_created": item.time_created,
                    "user_created": item.user_created,
                }
            )
        for item in list_task_02:
            list_task.append(
                {
                    "id": item.id,
                    "f5_device_ip": item.f5_device_ip.f5_device_ip,
                    "vs_name": item.vs_name,
                    "task_name": item.task_name,
                    "tag": item.tag,
                    "status": item.status,
                    "message": item.message,
                    "time_created": item.time_created,
                    "user_created": item.user_created,
                }
            )
        context = {"list_task": list_task}
        return context

class F5TaskUpdateView(UpdateView):
    model = F5CreateVirtualServer
    template_name = "f5/tasks/update.html"
    success_url = reverse_lazy("f5_list_task")

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self):
        task_name = self.kwargs["task_name"]
        task_id = self.kwargs["task_id"]
        if task_name == "create-virtual-server":
            self.form_class = F5CreateVirtualServerForm
            object = F5CreateVirtualServer.objects.get(pk=task_id)
            return object
        elif task_name == "create-limit-connection":
            self.form_class = F5LimitConnectionFormUpdate
            object = F5LimitConnection.objects.get(pk=task_id)
            return object

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(F5TaskUpdateView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class F5TaskDeleteView(DeleteView):
    model = F5CreateVirtualServer
    template_name = "f5/tasks/list.html"
    success_url = reverse_lazy("f5_list_task")

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self):
        task_name = self.kwargs["task_name"]
        task_id = self.kwargs["task_id"]
        if task_name == "create-virtual-server":
            object = F5CreateVirtualServer.objects.get(pk=task_id)
            return object
        elif task_name == "create-limit-connection":
            object = F5LimitConnection.objects.get(pk=task_id)
            return object


class F5VirtualServerPermissionUpdateView(UpdateView):
    model = F5VirtualServer
    form_class = F5VirtualServerPermissionForm
    template_name = "f5/permission/update.html"
    success_url = reverse_lazy("f5_list_permission")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="f5/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class F5VirtualServerPermissionListView(ListView):
    model = F5VirtualServer
    context_object_name = "objects"
    template_name = "f5/permission/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    
class F5VirtualServerListView(ListView):
    model = F5VirtualServer
    context_object_name = "objects"
    template_name = "f5/virtual-server/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
class F5VirtualServerUpdateView(UpdateView):
    model = F5VirtualServer
    form_class = F5VirtualServerForm
    template_name = "f5/virtual-server/update.html"
    success_url = reverse_lazy("f5_list_virtual_server")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="f5/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context
    

class F5LimitConnectionCreateView(CreateView):
    model = F5LimitConnection
    form_class = F5LimitConnectionForm
    template_name = "f5/tasks/limit-connection/create.html"
    success_url = reverse_lazy("f5_list_task")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Create success")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(F5LimitConnectionCreateView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context


class F5DeviceCreateView(CreateView):
    model = F5Device
    form_class = F5DeviceForm
    template_name = "f5/device/create.html"
    success_url = reverse_lazy("f5_list_device")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="f5/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Create success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context
    

class F5VirtualServerDeleteView(DeleteView):
    model = F5VirtualServer
    template_name = "f5/virtual-server/list.html"
    success_url = reverse_lazy("f5_list_virtual_server")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="f5/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)


class F5DeviceUpdateView(UpdateView):
    model = F5Device
    form_class = F5DeviceForm
    template_name = "f5/device/update.html"
    success_url = reverse_lazy("f5_list_device")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="f5/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class F5DeviceDeleteView(DeleteView):
    model = F5Device
    template_name = "f5/device/list.html"
    success_url = reverse_lazy("f5_list_device")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="f5/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)


class F5DeviceListView(ListView):
    model = F5Device
    context_object_name = "objects"
    template_name = "f5/device/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class F5CreateVirtualServerDetailView(DetailView):
    model = F5CreateVirtualServer
    template_name = "f5/tasks/virtual-server/detail.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class F5CreateVirtualServerListView(ListView):
    model = F5CreateVirtualServer
    context_object_name = "objects"
    template_name = "f5/tasks/virtual-server/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class F5CreateVirtualServerCreateView(CreateView):
    model = F5CreateVirtualServer
    form_class = F5CreateVirtualServerForm
    template_name = "f5/tasks/virtual-server/create.html"
    success_url = reverse_lazy("f5_create_virtual_server_list")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="f5/403.html")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context


class F5TemplateUpdateView(UpdateView):
    model = F5Template
    form_class = F5TemplateForm
    template_name = "f5/template/update.html"
    success_url = reverse_lazy("f5_list_template")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="f5/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class F5TemplateDeleteView(DeleteView):
    model = F5Template
    template_name = "f5/template/list.html"
    success_url = reverse_lazy("f5_list_template")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="f5/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)


class F5TemplateListView(ListView):
    model = F5Template
    context_object_name = "objects"
    template_name = "f5/template/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class F5TemplateCreateView(CreateView):
    model = F5Template
    form_class = F5TemplateForm
    template_name = "f5/template/create.html"
    success_url = reverse_lazy("f5_list_template")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="f5/403.html")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context


class F5TemplateDetailView(DetailView):
    model = F5Template
    template_name = "f5/template/detail.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    

@login_required()
def f5_database_export(request):
    form = F5ExportForm
    data = {"form": form}
    try:
        if request.method == "POST":
            form = F5ExportForm(request.POST)
            if form.is_valid():
                select_id = form.data['database_table']
                if select_id == '1':
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="virtual-server.csv"'
                    queryset = F5VirtualServer.objects.all()
                    writer = csv.writer(response)
                    writer.writerow([
                        'f5_device_ip',
                        'virtual_server',
                        'virtual_ip',
                        'virtual_port',
                        'client_ssl_profile',
                        'server_ssl_profile',
                        'service_dns',
                        'service_owner',
                        'center_head'
                    ])
                    for item in queryset:
                        writer.writerow([
                            item.f5_device_ip,
                            item.vs_name,
                            item.vs_ip,
                            item.vs_port,
                            item.client_ssl_profile,
                            item.server_ssl_profile,
                            item.service_dns_name,
                            item.service_owner,
                            item.center_head
                        ])
                    return response
    except Exception as error:
        messages.add_message(request, constants.ERROR, error)
    return render(request, template_name="f5/export/index.html", context=data)


def f5_update_multiple_virtual_server(request):
    try:
        if request.method == 'POST' and request.FILES.get('upload-file'):
            uploaded_file = request.FILES['upload-file']
            wb = openpyxl.load_workbook(uploaded_file)
            worksheet_01 = wb["VirtualServer"]
            for item in worksheet_01.iter_rows(min_row=2, values_only=True):
                item = ["" if i is None else i for i in item]
                f5_device_ip = item[0]	
                vs_name = item[1]	
                vs_ip = item[2]	
                vs_port = item[3]	
                client_ssl_profile = item[4]	
                server_ssl_profile = item[5]	
                service_dns = item[6]	
                service_owner = item[7]	
                center_head = item[8]	

                checklist01 = F5VirtualServer.objects.filter(f5_device_ip__f5_device_ip=f5_device_ip).count()
                checklist02 = F5VirtualServer.objects.filter(vs_name=vs_name).count()
                if checklist01 > 0 and checklist02 > 0:
                    object, created = F5VirtualServer.objects.update_or_create(
                        f5_device_ip=F5Device.objects.get(f5_device_ip=f5_device_ip),
                        vs_name=vs_name,
                        defaults={
                            'client_ssl_profile': client_ssl_profile,
                            'server_ssl_profile': server_ssl_profile,
                            'service_dns_name': service_dns,
                            'service_owner': service_owner,
                            'center_head': center_head
                        }
                    )
                    object.group_permission.set(Group.objects.filter(name="ADMIN"))
                    object.save()
            messages.add_message(request, constants.SUCCESS, 'Upload file success')
    except Exception as error:
        messages.add_message(request, constants.ERROR, f'An error occurred: {error}')
    return render(request, 'f5/virtual-server/update-multiple.html')

@login_required()
def checkpoint_dashboard(request):
    db_title = {
        "db_01": "Count rule by status",
        "db_02": "Count rule by user created",
    }
    return render(request, template_name="checkpoint/dashboard/index.html", context=db_title)


@login_required()
def fmc_dashboard(request):
    db_title = {
        "db_01": "Count rule by status",
        "db_02": "Count rule by user created",
    }
    return render(request, template_name="fmc/dashboard/index.html", context=db_title)


########################

class FMCRuleView(TemplateView):
    template_name = "fmc/access_rule/create.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)


class FMCPolicyCreateView(CreateView):
    model = FMCPolicy
    form_class = FMCPolicyForm
    template_name = "fmc/policy/create.html"
    success_url = reverse_lazy("fmc_list_policy")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Create success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context


class FMCPolicyListView(ListView):
    model = FMCPolicy
    context_object_name = "objects"
    template_name = "fmc/policy/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class FMCPolicyUpdateView(UpdateView):
    model = FMCPolicy
    form_class = FMCPolicyForm
    template_name = "fmc/policy/update.html"
    success_url = reverse_lazy("fmc_list_policy")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context
    

class FMCPolicyDeleteView(DeleteView):
    model = FMCPolicy
    template_name = "fmc/policy/list.html"
    success_url = reverse_lazy("fmc_list_policy")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)


class FMCSiteCreateView(CreateView):
    model = FMCSite
    form_class = FMCSiteForm
    template_name = "fmc/site/create.html"
    success_url = reverse_lazy("fmc_list_site")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Create success")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context
    

class FMCSiteListView(ListView):
    model = FMCSite
    context_object_name = "objects"
    template_name = "fmc/site/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class FMCSiteUpdateView(UpdateView):
    model = FMCSite
    form_class = FMCSiteForm
    template_name = "fmc/site/update.html"
    success_url = reverse_lazy("fmc_list_site")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class FMCSiteDeleteView(DeleteView):
    model = FMCSite
    template_name = "fmc/site/list.html"
    success_url = reverse_lazy("fmc_list_site")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)

# gateway
class FMCGatewayCreateView(CreateView):
    model = FMCGateway
    form_class = FMCGatewayForm
    template_name = "fmc/gateway/create.html"
    success_url = reverse_lazy("fmc_list_gateway")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Create success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context


class FMCGatewayListView(ListView):
    model = FMCGateway
    context_object_name = "objects"
    template_name = "fmc/gateway/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class FMCGatewayUpdateView(UpdateView):
    model = FMCGateway
    form_class = FMCGatewayForm
    template_name = "fmc/gateway/update.html"
    success_url = reverse_lazy("fmc_list_gateway")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class FMCGatewayDeleteView(DeleteView):
    model = FMCGateway
    template_name = "fmc/gateway/list.html"
    success_url = reverse_lazy("fmc_list_gateway")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)
# endgateway


class FMCRuleListView(ListView):
    model = FMCRule
    context_object_name = "objects"
    template_name = "fmc/access_rule/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            "list_rule_created": FMCRule.objects.filter(Q(status="Created") | Q(status="Install-Only")),
            "list_rule_process": FMCRule.objects.filter(status="Processing"),
            "list_rule_success": FMCRule.objects.filter(status="Success").order_by("-id")[:500],
            "list_rule_failed": FMCRule.objects.filter(status="Failed"),
        }
        return context


class FMCRuleDeleteView(DeleteView):
    model = FMCRule
    template_name = "fmc/site/list.html"
    success_url = reverse_lazy("fmc_list_task_access_rule")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)


class FMCRuleDetailView(DetailView):
    model = FMCRule
    template_name = "fmc/access_rule/detail.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class FMCRuleUpdateView(UpdateView):
    model = FMCRule
    form_class = FMCRuleForm
    template_name = "fmc/access_rule/update.html"
    success_url = reverse_lazy("fmc_list_task_access_rule")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context
##domain

class FMCDomainCreateView(CreateView):
    model = FMCDomain
    form_class = FMCDomainForm
    template_name = "fmc/domain/create.html"
    success_url = reverse_lazy("fmc_list_domain")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Create success")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context


class FMCDomainListView(ListView):
    model = FMCDomain
    context_object_name = "objects"
    template_name = "fmc/domain/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class FMCDomainUpdateView(UpdateView):
    model = FMCDomain
    form_class = FMCDomainForm
    template_name = "fmc/domain/update.html"
    success_url = reverse_lazy("fmc_list_domain")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class FMCDomainDeleteView(DeleteView):
    model = FMCDomain
    template_name = "fmc/domain/list.html"
    success_url = reverse_lazy("fmc_list_domain")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="fmc/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)

## local user
class CheckpointLocalUserCreateView(FormView):
    form_class = CheckpointLocalUserBulkForm
    template_name = "checkpoint/local-user/create.html"
    success_url = reverse_lazy("checkpoint_list_task_local_user")

    @transaction.atomic
    def form_valid(self, form):
        data = form.cleaned_data
        user_names = [name.strip() for name in data['user_names'].splitlines() if name.strip()]
        
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for username in user_names:
            try:
                try:
                    user = CheckpointLocalUser.objects.get(user_name=username)
                    created = False
                except CheckpointLocalUser.DoesNotExist:
                    user = CheckpointLocalUser(
                        user_name=username,
                        user_created=self.request.user.username
                    )
                    created = True

                if created:
                    user.template = data['template']
                    user.is_partner = data['is_partner']
                    user.password = data['password'] or None
                    user.email = data['email'] or None
                    user.phone_number = data['phone_number']
                    user.expiration_date = data['expiration_date'].strftime("%Y-%m-%d") if data['expiration_date'] else None
                    user.custom_group = data['custom_group'] or None
                    user.status = data['status'] or 'Created'
                    user.save()
                    
                    if data['user_group']:
                        user.user_group.set(data['user_group'])
                    
                    created_count += 1
                else:
                    update_fields = []
                    
                    if data['template'] is not None:
                        user.template = data['template']
                        update_fields.append('template')
                    
                    if data['is_partner'] is not None:
                        user.is_partner = data['is_partner']
                        update_fields.append('is_partner')
                    
                    if data['password']:
                        user.password = data['password']
                        update_fields.append('password')
                    
                    if data['email']:
                        user.email = data['email']
                        update_fields.append('email')
                    
                    if data['phone_number'] is not None:
                        user.phone_number = data['phone_number']
                        update_fields.append('phone_number')
                    
                    if data['expiration_date'] is not None:
                        user.expiration_date = data['expiration_date'].strftime("%Y-%m-%d")
                        update_fields.append('expiration_date')
                    
                    if data['custom_group'] is not None:
                        user.custom_group = data['custom_group'] or None
                        update_fields.append('custom_group')
                    
                    if data['status']:
                        user.status = data['status']
                        update_fields.append('status')
                    
                    if update_fields:
                        user.save(update_fields=update_fields)
                    
                    if data['user_group'] is not None:
                        user.user_group.set(data['user_group'])
                    
                    updated_count += 1
                        
            except IntegrityError as e:
                skipped_count += 1
                messages.warning(self.request, f"Process error with {username}: {str(e)}")
            except Exception as e:
                skipped_count += 1
                messages.warning(self.request, f"Process error with {username}: {str(e)}")

        msg = f"Success: {created_count} Created, {updated_count} Updated"
        if skipped_count:
            msg += f", {skipped_count} Skiped"
        messages.success(self.request, msg)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create CheckpointLocalUser"
        return context

class CheckpointLocalUserListView(ListView):
    model = CheckpointLocalUser
    context_object_name = "objects"
    template_name = "checkpoint/local-user/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CheckpointLocalUserUpdateView(UpdateView):
    model = CheckpointLocalUser
    form_class = CheckpointLocalUserForm
    template_name = "checkpoint/local-user/update.html"
    success_url = reverse_lazy("checkpoint_list_task_local_user")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class CheckpointLocalUserDeleteView(DeleteView):
    model = CheckpointLocalUser
    template_name = "checkpoint/local-user/list.html"
    success_url = reverse_lazy("checkpoint_list_task_local_user")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)
    

class CheckpointLocalUserDetailView(DetailView):
    model = CheckpointLocalUser
    template_name = "checkpoint/local-user/detail.html"
    exclude_fields = ["password", "smc"]

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        fields = [(field.verbose_name, field.value_from_object(obj))
                  for field in obj._meta.fields if field.verbose_name not in self.exclude_fields]
        context['fields'] = fields
        context['banner'] = f'{self.model.__name__} detail informations'
        return context
    
## local user template

class CheckpointLocalUserTemplateCreateView(CreateView):
    model = CheckpointLocalUserTemplate
    form_class = CheckpointLocalUserTemplateForm
    template_name = "checkpoint/local-user-template/create.html"
    success_url = reverse_lazy("checkpoint_list_local_user_template")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Create success")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context


class CheckpointLocalUserTemplateListView(ListView):
    model = CheckpointLocalUserTemplate
    context_object_name = "objects"
    template_name = "checkpoint/local-user-template/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CheckpointLocalUserTemplateUpdateView(UpdateView):
    model = CheckpointLocalUserTemplate
    form_class = CheckpointLocalUserTemplateForm
    template_name = "checkpoint/local-user-template/update.html"
    success_url = reverse_lazy("checkpoint_list_local_user_template")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class CheckpointLocalUserTemplateDeleteView(DeleteView):
    model = CheckpointLocalUserTemplate
    template_name = "checkpoint/local-user-template/list.html"
    success_url = reverse_lazy("checkpoint_list_local_user_template")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)
    

class CheckpointLocalUserTemplateDetailView(DetailView):
    model = CheckpointLocalUserTemplate
    template_name = "checkpoint/local-user-template/detail.html"
    exclude_fields = ["password", "smc"]

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        fields = [(field.verbose_name, field.value_from_object(obj))
                  for field in obj._meta.fields if field.verbose_name not in self.exclude_fields]
        context['fields'] = fields
        context['banner'] = f'{self.model.__name__} detail informations'
        return context
    
###

class CheckpointEmailAlertTemplateCreateView(CreateView):
    model = CheckpointEmailAlertTemplate
    form_class = CheckpointEmailAlertTemplateForm
    template_name = "checkpoint/email-alert-template/create.html"
    success_url = reverse_lazy("checkpoint_list_email_alert_template")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Create success")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Create {self.model.__name__}"
        return context


class CheckpointEmailAlertTemplateListView(ListView):
    model = CheckpointEmailAlertTemplate
    context_object_name = "objects"
    template_name = "checkpoint/email-alert-template/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CheckpointEmailAlertTemplateUpdateView(UpdateView):
    model = CheckpointEmailAlertTemplate
    form_class = CheckpointEmailAlertTemplateForm
    template_name = "checkpoint/email-alert-template/update.html"
    success_url = reverse_lazy("checkpoint_list_email_alert_template")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = f"Update {self.model.__name__}"
        return context


class CheckpointEmailAlertTemplateDeleteView(DeleteView):
    model = CheckpointEmailAlertTemplate
    template_name = "checkpoint/email-alert-template/list.html"
    success_url = reverse_lazy("checkpoint_list_email_alert_template")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="ADMIN").exists():
            return render(request, template_name="checkpoint/common/403.html")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)
    

class CheckpointEmailAlertTemplateDetailView(DetailView):
    model = CheckpointEmailAlertTemplate
    template_name = "checkpoint/email-alert-template/detail.html"
    exclude_fields = ["password", "smc"]

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        fields = [(field.verbose_name, field.value_from_object(obj))
                  for field in obj._meta.fields if field.verbose_name not in self.exclude_fields]
        context['fields'] = fields
        context['banner'] = f'{self.model.__name__} detail informations'
        return context