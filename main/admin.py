from django.contrib import admin
from django.contrib.admin import ModelAdmin
from main.models import Contest, Problem, Submission

class ContestAdmin(ModelAdmin):
	list_display = ("ccode", "title", "can_view", "can_submit")

class ProblemAdmin(ModelAdmin):
	list_display = ("pcode", "title", "contest")

class SubmissionAdmin(ModelAdmin):
	list_display = ("id", "problem", "user", "lang", "get_status_str")

admin.site.register(Contest, ContestAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Submission, SubmissionAdmin)
