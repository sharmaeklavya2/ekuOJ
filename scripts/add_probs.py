"""
This module has functions which syncs problems data in database with data in OJ_data
"""

import os
FILE_PATH = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(FILE_PATH))
import sys
if BASE_DIR not in sys.path:
	sys.path.append(BASE_DIR)

import json

def add_prob(prob_path, contest=None):
	pcode = os.path.basename(prob_path)
	if contest==None:
		ccode = os.path.basename(os.path.dirname(prob_path))
		contest = Contest.objects.get_or_create(ccode=ccode)[0]
	(problem, created) = Problem.objects.get_or_create(pcode=pcode, contest=contest)
	title_path = os.path.join(prob_path, "title.txt")
	data_path = os.path.join(prob_path, "data.json")
	try:
		problem.title = open(title_path).read().strip()
	except FileNotFoundError:
		pass
	try:
		prob_data = json.load(open(data_path))
		problem.source_lim = prob_data.get("source_lim", None)
	except FileNotFoundError:
		pass
	except ValueError as e:
		print("The following error was encountered while reading", os.path.join(ccode, pcode, "data.json")+".", "The file has been ignored.")
		print(e)
	problem.save()
	return created

def add_contest(contest_path):
	# create contest object in db
	ccode = os.path.basename(contest_path)
	(contest, created) = Contest.objects.get_or_create(ccode=ccode)
	title_path = os.path.join(contest_path, "title.txt")
	try:
		contest.title = open(title_path).read().strip()
	except FileNotFoundError:
		pass
	contest.save()

	# add problems to db
	pcodes = os.listdir(contest_path)
	for pcode in pcodes:
		prob_path = os.path.join(contest_path, pcode)
		add_prob(prob_path, contest)
	return created

FILE_NAME = os.path.basename(FILE_PATH)
if __name__=="__main__":
	USAGE_STR = "usage: python3 " + FILE_NAME + " <contest_codes>"
else:
	USAGE_STR = "No contests specified"
CONTESTS_DIR_PATH = os.path.join(BASE_DIR, "OJ_data", "contests")

import sys

def main(*args):
	if len(args)==0:
		print(USAGE_STR, file=sys.stderr)
	else:
		for ccode in args:
			contest_path = os.path.join(CONTESTS_DIR_PATH, ccode)
			created = add_contest(contest_path)
			if created:
				print("Added contest", ccode)
			else:
				print("Updated contest", ccode)

if __name__=="__main__":
	# set up django
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_conf.settings")
	print("Setting up Django ...", flush=True, end='')
	import django
	django.setup()
	print(" done")

from main.models import Problem, Contest

if __name__=="__main__":
	main(*(sys.argv[1:]))
