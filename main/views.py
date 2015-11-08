from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from main.models import Contest, Problem, Submission
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
import os

def base_response(request, body, title=None):
	context_dict = {"base_body": body}
	if title:
		context_dict["base_title"] = title
	return render(request, "base.html", context_dict)

def index(request):
	return base_response(request, "This site is under construction")

@login_required
def submit(request, ccode, pcode):
	contest = get_object_or_404(Contest, ccode=ccode)
	problem = get_object_or_404(Problem, pcode=pcode, contest=contest)
	if not contest.can_submit:
		raise Http404("Submission not allowed")
	context_dict = {"contest": contest, "problem": problem}
	source_lim = problem.source_lim
	if source_lim==None:
		source_lim = settings.DEFAULT_SOURCE_LIM
	context_dict["source_lim"] = source_lim
	context_dict["lang_info"] = sorted(settings.LANG_INFO.items())

	if request.method=="POST":
		if "lang" not in request.POST:
			context_dict["error_msg"] = "Please specify a programming language"
		else:
			lang = request.POST["lang"]
			context_dict["lang"] = lang
			if not lang:
				context_dict["error_msg"] = "Please specify a programming language"
			elif lang not in settings.LANG_INFO:
				context_dict["error_msg"] = "This programming language is unknown or not supported"
			elif "file" not in request.FILES:
				context_dict["error_msg"] = "Submission must include a file"
			else:
				ufile = request.FILES["file"]
				if ufile.size>source_lim:
					context_dict["error_msg"] = "The uploaded file exceeds source code limit"
				else:
					sub = Submission(lang=lang, user=request.user, problem=problem, submit_time=timezone.now())
					sub.set_status_from_str("PEND")
					sub.save()
					sub.fname = str(sub.id)+"."+settings.LANG_INFO[lang]["ext"]
					fpath = sub.get_path()
					if not os.path.exists(os.path.dirname(fpath)):
						os.makedirs(os.path.dirname(fpath), mode=0o770)
					with open(fpath, "wb") as dest_file:
						for chunk in ufile.chunks():
							dest_file.write(chunk)
					sub.save()
					sub.run_code()
					return HttpResponseRedirect(reverse("main:submission_status", args=(sub.id,)))
	return render(request, "submit.html", context_dict)

def submission_status(request, sid):
	sub = get_object_or_404(Submission, id=sid)
	context_dict = {"sub": sub}
	return render(request, "submission_status.html", context_dict)
