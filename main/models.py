from django.db import models
from django.contrib.auth.models import User

class Contest(models.Model):
	ccode = models.CharField("Contest Code", max_length=30, unique=True, blank=False)
	title = models.TextField("Contest Title", blank=True)
	can_view = models.BooleanField("Can problem statements be viewed", default=True)
	can_submit = models.BooleanField("Can solutions be submitted", default=True)
	def __str__(self):
		return self.ccode

class Problem(models.Model):
	pcode = models.CharField("Problem Code", max_length=30, blank=False)
	title = models.TextField("Problem Title", blank=True)
	contest = models.ForeignKey(Contest)
	source_lim = models.IntegerField("Source code limit", null=True)
	def __str__(self):
		return self.pcode

class Submission(models.Model):
	lang = models.CharField("Language", max_length=30, blank=False)
	fname = models.CharField("File name", max_length=255, blank=False)
	user = models.ForeignKey(User)
	problem = models.ForeignKey(Problem)
	success = models.BooleanField(default=False)
	def __str__(self):
		return str((self.pk(), self.user.username, str(self.problem.pcode), self.lang))
