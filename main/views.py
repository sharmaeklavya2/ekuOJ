from django.shortcuts import render

def base_response(request, body, title=None):
	context_dict = {"base_body": body}
	if title:
		context_dict["base_title"] = title
	return render(request, "base.html", context_dict)

def index(request):
	return base_response(request, "This site is under construction")
