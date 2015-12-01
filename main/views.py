from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from main.models import Contest, Problem, Submission
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta, datetime
import os
import markdown

def base_response(request, body, title=None):
	context_dict = {"base_body": body}
	if title:
		context_dict["base_title"] = title
	return render(request, "base.html", context_dict)

def index(request):
	context_dict = {}
	context_dict["main_contest_url"] = Contest.objects.get(ccode="MAIN").get_view_url()
	context_dict["contests"] = Contest.objects.all()
	return render(request, "index.html", context_dict)

@login_required
def submit(request, ccode, pcode):
	contest = get_object_or_404(Contest, ccode=ccode)
	problem = get_object_or_404(Problem, pcode=pcode, contest=contest)
	if not problem.get_can_submit():
		raise PermissionDenied
	context_dict = {"contest": contest, "problem": problem}
	source_lim = problem.get_source_lim()
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
	context_dict["lang_name"] = settings.LANG_INFO[sub.lang]["name"]
	return render(request, "submission_status.html", context_dict)

def get_samples(prob_path):
	files = {}
	in_dir_path = os.path.join(prob_path, "in")
	out_dir_path = os.path.join(prob_path, "out")

	try:
		sin = open(os.path.join(in_dir_path, "sample.txt")).read()
		sout = open(os.path.join(out_dir_path, "sample.txt")).read()
		files["sample.txt"] = {"in": sin, "out": sout}
	except FileNotFoundError:
		pass

	for (curr_dir_path, dir_names, file_names) in os.walk(os.path.join(in_dir_path, "sample")):
		rel_path = os.path.relpath(curr_dir_path, in_dir_path)
		for fname in file_names:
			in_file_path = os.path.join(curr_dir_path, fname)
			rel_file_path = os.path.join(rel_path, fname)
			out_file_path = os.path.join(out_dir_path, rel_file_path)
			try:
				sout = open(out_file_path).read()
				sin = open(in_file_path).read()
				files[rel_file_path] = {"in": sin, "out": sout}
			except FileNotFoundError:
				pass
	return files

def view_problem(request, ccode, pcode):
	contest = get_object_or_404(Contest, ccode=ccode)
	problem = get_object_or_404(Problem, pcode=pcode, contest=contest)
	if not problem.get_can_view():
		raise PermissionDenied("Disallowed")
	context_dict = {"contest": contest, "problem": problem}

	prob_path = problem.get_path()
	try:
		prob_md = open(os.path.join(prob_path, "problem.md")).read().strip()
		context_dict["prob_body"] = markdown.markdown(prob_md)
	except FileNotFoundError:
		context_dict["prob_body"] = "The problem statement has been removed"
	context_dict["samples"] = get_samples(prob_path)

	return render(request, "view_problem.html", context_dict)

def view_contest(request, ccode):
	contest = get_object_or_404(Contest, ccode=ccode)
	context_dict = {"contest": contest}
	if contest.get_can_view():
		problems = Problem.objects.filter(contest=contest)
	else:
		problems = []
	scode_dict = Submission.STATUS_CODES
	for p in problems:
		p.pass_subs = Submission.objects.filter(problem=p, status=scode_dict["PASS"]).count()
		p.subs = Submission.objects.filter(problem=p).count()
		if request.user.is_authenticated():
			user_subs = Submission.objects.filter(user=request.user, problem=p)
			if user_subs.filter(status=scode_dict["PASS"]).exists():
				p.status = "PASS"
			elif user_subs.filter(Q(status=scode_dict["FAIL"]) or Q(status=scode_dict["CMPLE"])).exists():
				p.status = "FAIL"
			elif user_subs.filter(status=scode_dict["PEND"]).exists():
				p.status = "PEND"
			else:
				p.status = "NA"
	context_dict["problems"] = problems
	return render(request, "view_contest.html", context_dict)

def status(request):
	arg_dict = {
		"user": "user__username",
		"ccode": "problem__contest__ccode",
		"pcode": "problem__pcode",
		"status": "status",
		"lang": "lang"
	}
	context_dict = {}
	kwargs={}
	for arg in arg_dict:
		if arg in request.GET:
			kwargs[arg] = request.GET[arg]

	if "status" in kwargs:
		try:
			kwargs["status"] = Submission.STATUS_CODES[kwargs["status"].upper()]
		except KeyError:
			kwargs["status"] = -1
	kwargs = {arg_dict[key]: value for (key,value) in kwargs.items()}

	order_by_args = []
	sort_args = (",".join(request.GET.getlist("sort"))).split(",")
	for arg in sort_args:
		if arg.startswith("-"):
			arg = arg[1:]
			reverse_str = "-"
		else:
			reverse_str = ""
		if arg in arg_dict.keys():
			order_by_args.append(reverse_str+arg_dict[arg])
		if arg == "id":
			order_by_args.append(reverse_str+arg)

	submissions = Submission.objects.filter(problem__contest__can_view=True, problem__can_view=True)
	if kwargs:
		submissions = submissions.filter(**kwargs)
	if order_by_args:
		submissions = submissions.order_by(*order_by_args)
	else:
		submissions = submissions.order_by("-id")
	context_dict["submissions"] = submissions
	return render(request, "status.html", context_dict)
