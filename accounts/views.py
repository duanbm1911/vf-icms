from django.contrib.auth import logout as auth_logout, login as auth_login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import ProtectedError
from django.views.generic import UpdateView, DeleteView, DetailView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate
from django.contrib.messages import constants
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from accounts.models import *
from accounts.forms import *
from io import BytesIO
import base64
import pyotp
import qrcode

# Create your views here.


def get_client_ip(request):
    client_ip = str()
    if request.META.get("HTTP_CLIENT_IP") is not None:
        client_ip = request.META.get("HTTP_CLIENT_IP")
    else:
        client_ip = request.META.get("REMOTE_ADDR")
    return client_ip


def logout(request):
    auth_logout(request)
    return redirect("/accounts/login")


@login_required()
def change_password(request):
    if request.method == "POST":
        form = ValidatingPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, "Your password was successfully updated!")
            return redirect("/")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = ValidatingPasswordChangeForm(request.user)
    return render(request, "user/change_password.html", {"form": form})


def login(request):
    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        otp = request.POST.get("otp")
        client_ip = get_client_ip(request)
        getlist = ClientLoginFailedSession.objects.filter(
            client_ip=client_ip, username=username
        ).count()
        login_failed_count = 0
        if getlist > 0:
            obj = ClientLoginFailedSession.objects.get(
                client_ip=client_ip, username=username
            )
            login_failed_count = obj.failed_count
        if login_failed_count <= 5:
            retries_login_count = 5 - login_failed_count
            user = authenticate(username=username, password=password)
            verify_otp_result = verify_otp(user, otp)
            if user is not None and verify_otp_result:
                auth_login(request, user)
                login_failed = ClientLoginFailedSession.objects.filter(
                    client_ip=client_ip, username=username
                )
                login_failed.delete()
                return redirect("/")
            else:
                if login_failed_count <= 5:
                    if getlist > 0:
                        obj = ClientLoginFailedSession.objects.get(
                            client_ip=client_ip, username=username
                        )
                        failed_count = obj.failed_count
                        obj.failed_count = failed_count + 1
                        obj.save()
                    else:
                        obj = ClientLoginFailedSession(
                            client_ip=client_ip, username=username, failed_count=1
                        )
                        obj.save()
            messages.add_message(
                request,
                constants.ERROR,
                f"Login failed, The account will be locked after {retries_login_count} failed attempts ",
            )
        else:
            messages.add_message(
                request,
                constants.ERROR,
                f"Account: {username} has been locked, please contact with Administrator",
            )
    return render(request, "user/login.html")


def verify_otp(user, otp):
    try:
        obj = User.objects.get(username=user)
        model = UserOTP.objects.get(user=obj)
        otp_key = model.otp_key
        totp = pyotp.TOTP(otp_key)
        result = totp.verify(otp)
        return result
    except:
        return False


def register(request):
    if request.user.is_superuser:
        if request.method == "GET":
            form = RegisterForm()
        else:
            form = RegisterForm(request.POST)
            if form.is_valid():
                secret_key = pyotp.random_base32()
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                UserOTP.objects.update_or_create(
                    user = User.objects.get(username=user.username),
                    defaults = {
                        'otp_key': pyotp.random_base32(),
                        'qrcode_url': 1
                    }
                )
                messages.add_message(
                    request, constants.SUCCESS, "Register user success"
                )
                return redirect(reverse_lazy('list_user'))
        return render(request, "user/register.html", {"form": form})
    else:
        return render(request, template_name="403.html")


class UserListView(ListView):
    model = User
    context_object_name = "objects"
    template_name = "user/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            return render(self.request, template_name="403.html")
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = "List users"
        return context


def get_qrcode(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = UserSelectForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                try:
                    user_obj = User.objects.get(username=user)
                except:
                    msg = f"User: {user} does not exists"
                    messages.add_message(request, messages.ERROR, msg)
                else:
                    try:
                        user_otp_obj = UserOTP.objects.get(user=user_obj)
                    except:
                        msg = f"User: {user} does not have OTP key"
                        messages.add_message(request, messages.ERROR, msg)
                    else:
                        otp_key = user_otp_obj.otp_key
                        totp = pyotp.TOTP(otp_key)
                        uri = totp.provisioning_uri(name=str(user), issuer_name="ICMS Authenticate")
                        qr = qrcode.make(uri)
                        qr_image = BytesIO()
                        qr.save(qr_image)
                        qr_image.seek(0)
                        qr_code = base64.b64encode(qr_image.getvalue()).decode("utf-8")
                        return render(request, 'user/get_qrcode_result.html', {'qr_code': qr_code, 'user': user})
        else:
            form = UserSelectForm()
        return render(request, 'user/get_qrcode.html', {'form': form})
    else:
        return render(request, template_name="403.html")
    
    
class UserUpdateView(UpdateView):
    model = User
    form_class = EditUserForm
    template_name = 'user/update.html'
    success_url = reverse_lazy('list_user')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            return render(self.request, template_name="403.html")
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.user_created = str(self.request.user)
        messages.add_message(self.request, constants.SUCCESS, "Update success")
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return User.objects.get(pk=self.kwargs['pk']) 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banner'] = "Update User"
        return context
    
    
class UserDetailView(DetailView):
    model = User
    template_name = 'user/detail.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            return render(self.request, template_name="403.html")
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return User.objects.get(pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        fields = [(field.verbose_name, field.value_from_object(obj))
                  for field in obj._meta.fields]
        context['fields'] = fields
        context['banner'] = "User Detail"
        return context
    
    
class UserDeleteView(DeleteView):
    model = User
    template_name = 'user/list.html'
    success_url = reverse_lazy('list_user')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
            messages.add_message(
                self.request, constants.SUCCESS, "Delete success")
        except ProtectedError:
            messages.add_message(
                self.request, constants.ERROR, "This object has been protected"
            )
        except Exception as error:
            messages.add_message(self.request, constants.ERROR, error)
        return redirect(self.success_url)