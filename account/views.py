from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import EditProfileForm

#def base_response(request, body, title=None, h1=None):
#	context_dict = {"base_body": body}
#	if title:
#		context_dict["base_title"] = title
#	if h1:
#		context_dict["base_h1"] = h1
#	return render(request, "account/base.html", context_dict)

def login_view(request):
	context_dict = {}
	if request.method=="POST":
		next_url=""
		if "next" in request.POST:
			next_url = request.POST["next"]
		if next_url:
			context_dict["next"] = next_url
		if "uoe" in request.POST and "password" in request.POST and request.POST["uoe"] and request.POST["password"]:
			uoe = request.POST["uoe"]
			password = request.POST["password"]
			context_dict["uoe"] = uoe
			try:
				if "@" in uoe:
					username = User.objects.get(email=uoe).username
				else:
					username = uoe
				user = authenticate(username=username, password=password)
			except User.DoesNotExist:
				user = None
			if not user:
				context_dict["login_error"] = "Username or password is incorrect"
			elif not user.is_active:
				context_dict["login_error"] = "Your account has been disabled. Contact support."
			else:
				login(request, user)
				if not next_url:
					next_url = settings.LOGIN_REDIRECT_URL
				return HttpResponseRedirect(next_url)
		else:
			context_dict["login_error"] = "You must enter both username and password"
	elif request.method=="GET":
		if "next" in request.GET and request.GET["next"]:
			context_dict["next"] = request.GET["next"]
	return render(request, "account/login.html", context_dict)

def logout_view(request):
	if request.user.is_authenticated():
		logout(request)
	return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)

def register(request):
	context_dict = {}
	if request.method=="POST":
		if ("username" in request.POST and request.POST["username"]) and ("password" in request.POST and request.POST["password"]) and "email" in request.POST:
			username = request.POST["username"]
			password = request.POST["password"]
			email = request.POST["email"]
			context_dict["username"] = username
			context_dict["email"] = email
			if "@" in username:
				context_dict["register_error"] = "username cannot contain @"
			elif User.objects.filter(username=username).exists():
				context_dict["register_error"] = "A user with this username already exists"
			elif email and User.objects.filter(email=email).exists():
				context_dict["register_error"] = "A user with this email already exists"
			else:
				user = User(username=username, email=email)
				user.set_password(password)
				user.save()
				user = authenticate(username=username, password=password)
				login(request, user)
				return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
		else:
			context_dict["register_error"] = "You must fill out all fields"
	return render(request, "account/register.html", context_dict)

_not_impl_string = "This page is not yet implemented"

def index(request):
	return HttpResponseRedirect(reverse("account:account_info"))

@login_required
def account_info(request):
	return render(request, "account/account_info.html", {})

def public_profile(request, username):
	puser = get_object_or_404(User, username=username)
	context_dict = {"puser": puser}
	return render(request, "account/public_profile.html", context_dict)

@login_required
def edit_profile(request):
	context_dict = {}
	if request.method=="POST":
		form = EditProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			context_dict["ep_success"] = "Profile changed successsfully"
		else:
			context_dict["ep_error"] = "Invalid data received"
	else:
		form = EditProfileForm(instance=request.user)
	context_dict["form"] = form
	return render(request, "account/edit_profile.html", context_dict)

@login_required
def change_password(request):
	context_dict = {}
	if request.method=="POST":
		if "password" in request.POST and request.POST["password"]:
			password = request.POST["password"]
			request.user.set_password(password)
			request.user.save()
			user = authenticate(username=request.user.username, password=password)
			login(request, user)
			return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
		else:
			context_dict["cp_error"] = "You must fill out a password"
	return render(request, "account/change_password.html", context_dict)

def user_list(request):
	context_dict = {"user_list": list(User.objects.all())}
	return render(request, "account/user_list.html", context_dict)
