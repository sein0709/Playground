from django.contrib import admin

from .models import Assignment, Choice, Course, Question, Submission, SubmissionAnswer, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role")
    list_filter = ("role",)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "prompt", "question_type", "points", "order")
    list_filter = ("question_type",)
    inlines = [ChoiceInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "due_date", "published")
    list_filter = ("course", "published")
    inlines = [QuestionInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    filter_horizontal = ("instructors", "students")


class SubmissionAnswerInline(admin.TabularInline):
    model = SubmissionAnswer
    extra = 0


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "student", "submitted_at", "total_score", "published")
    list_filter = ("assignment", "published")
    inlines = [SubmissionAnswerInline]

# Register your models here.
