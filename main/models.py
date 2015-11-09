from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse

import os
from datetime import timedelta, datetime
import json

from OJL3 import judges

class Contest(models.Model):
	ccode = models.CharField("Contest Code", max_length=30, unique=True, blank=False)
	title = models.TextField("Contest Title", blank=True)
	can_view = models.BooleanField("Can problem statements be viewed", default=True)
	can_submit = models.BooleanField("Can solutions be submitted", default=True)
	def __str__(self):
		return self.ccode
	def get_name(self):
		if self.title:
			return self.title
		else:
			return self.ccode
	def get_path(self):
		return os.path.join(settings.OJ_DATA_DIR, "contests", self.ccode)
	def get_view_url(self):
		return reverse('main:view_contest', args=(self.ccode,))
	def get_absolute_url(self):
		return self.get_view_url()

class Problem(models.Model):
	pcode = models.CharField("Problem Code", max_length=30, blank=False)
	title = models.TextField("Problem Title", blank=True)
	contest = models.ForeignKey(Contest)
	source_lim = models.IntegerField("Source code limit", null=True)
	time_lim_s = models.IntegerField("Time limit", null=True)
	mem_lim_k = models.IntegerField("Memory limit", null=True)
	output_lim_k = models.IntegerField("Output limit", null=True)
	def __str__(self):
		return self.pcode
	def get_name(self):
		if self.title:
			return self.title
		else:
			return self.pcode
	def get_path(self):
		return os.path.join(self.contest.get_path(), self.pcode)
	def get_view_url(self):
		return reverse('main:view_problem', args=(self.contest.ccode, self.pcode))
	def get_submit_url(self):
		return reverse('main:submit', args=(self.contest.ccode, self.pcode))
	def get_absolute_url(self):
		return self.get_view_url()

	def get_source_lim(self):
		if self.source_lim==None:
			return settings.DEFAULT_SOURCE_LIM
		else:
			return self.source_lim
	def get_time_lim_s(self):
		if self.time_lim_s==None:
			return judges.DEFAULT_TIME_LIM_S
		else:
			return self.time_lim_s
	def get_mem_lim_k(self):
		if self.mem_lim_k==None:
			return judges.DEFAULT_MEM_LIM_K
		else:
			return self.mem_lim_k
	def get_output_lim_k(self):
		if self.output_lim_k==None:
			return judges.DEFAULT_OUTPUT_LIM_K
		else:
			return self.output_lim_k

class Submission(models.Model):
	lang = models.CharField("Language", max_length=30, blank=False)
	fname = models.CharField("File name", max_length=255, blank=False)
	user = models.ForeignKey(User)
	problem = models.ForeignKey(Problem)
	status = models.IntegerField()
	status_info = models.TextField(blank=True)
	submit_time = models.DateTimeField(null=True)
	STATUS_STRS = ("PASS", "FAIL", "CMPLE", "PEND")
	STATUS_CODES = {"PASS": 0, "FAIL": 1, "CMPLE": 2, "PEND": 3}
	def __str__(self):
		return str((self.id, self.user.username, str(self.problem.pcode), self.lang))
	def get_path(self):
		return os.path.join(settings.OJ_DATA_DIR, "submissions", self.user.username, self.fname)
	def get_status_str(self):
		return Submission.STATUS_STRS[self.status]
	def set_status_from_str(self, status_str):
		self.status = Submission.STATUS_STRS.index(status_str)
	def get_status_url(self):
		return reverse('main:submission_status', args=(str(self.id),))
	def run_code(self):
		source_path = self.get_path()
		(status, result) = judges.send_to_IOCJ(prob_path=self.problem.get_path(), submission_code=str(self.id), lang=self.lang, source_path=source_path, overwrite_prison_cell=True)
		if status in Submission.STATUS_STRS:
			self.set_status_from_str(status)
			result_path = source_path+".result"
			if status=="CMPLE":
				self.status_info = result
			else:
				self.status_info = json.dumps(result, indent=2)
			with open(result_path, "w") as resfile:
				json.dump((status, result), resfile, indent=2)
		else:
			raise ValueError("OJL3 returned invalid status in "+self.id)
		self.save()
