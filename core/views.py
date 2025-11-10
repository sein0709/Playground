import csv
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import (
    AssignmentForm,
    CourseForm,
    QuestionForm,
    SubmissionFeedbackForm,
    SubmissionForm,
)
from .models import Assignment, Choice, Course, Question, Submission, SubmissionAnswer, User


class UserLoginView(LoginView):
    template_name = "registration/login.html"


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("login")


@login_required
def dashboard(request):
    if request.user.is_instructor():
        return redirect("instructor_dashboard")
    return redirect("student_dashboard")


@role_required(User.Roles.INSTRUCTOR)
def instructor_dashboard(request):
    courses = request.user.courses_instructing.prefetch_related("assignments")
    assignments = Assignment.objects.filter(course__instructors=request.user).prefetch_related("course")
    pending_submissions = (
        Submission.objects.filter(assignment__course__instructors=request.user)
        .filter(answers__question__question_type=Question.QuestionTypes.FREE_RESPONSE, answers__score__isnull=True)
        .distinct()
    )
    context = {
        "courses": courses,
        "assignments": assignments,
        "pending_submissions": pending_submissions,
    }
    return render(request, "core/instructor_dashboard.html", context)


@role_required(User.Roles.INSTRUCTOR)
def course_list(request):
    courses = request.user.courses_instructing.all()
    return render(request, "core/course_list.html", {"courses": courses})


@role_required(User.Roles.INSTRUCTOR)
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        form.fields["students"].queryset = User.objects.filter(role=User.Roles.STUDENT)
        if form.is_valid():
            course = form.save()
            course.instructors.add(request.user)
            messages.success(request, "Course created successfully.")
            return redirect("course_list")
    else:
        form = CourseForm()
        form.fields["students"].queryset = User.objects.filter(role=User.Roles.STUDENT)
    return render(request, "core/course_form.html", {"form": form})


@role_required(User.Roles.INSTRUCTOR)
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, instructors=request.user)
    return render(request, "core/course_detail.html", {"course": course})


@role_required(User.Roles.INSTRUCTOR)
def assignment_create(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        form.fields["course"].queryset = request.user.courses_instructing.all()
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, "Assignment created. Add questions next.")
            return redirect("assignment_detail", pk=assignment.pk)
    else:
        form = AssignmentForm()
        form.fields["course"].queryset = request.user.courses_instructing.all()
    return render(request, "core/assignment_form.html", {"form": form})


@role_required(User.Roles.INSTRUCTOR)
def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, course__instructors=request.user)
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        form.fields["course"].queryset = request.user.courses_instructing.all()
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated.")
            return redirect("assignment_detail", pk=assignment.pk)
    else:
        form = AssignmentForm(instance=assignment)
        form.fields["course"].queryset = request.user.courses_instructing.all()
    return render(request, "core/assignment_form.html", {"form": form, "assignment": assignment})


@role_required(User.Roles.INSTRUCTOR)
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, course__instructors=request.user)
    questions = assignment.questions.prefetch_related("choices")
    submissions = assignment.submissions.select_related("student")
    return render(
        request,
        "core/assignment_detail.html",
        {"assignment": assignment, "questions": questions, "submissions": submissions},
    )


@role_required(User.Roles.INSTRUCTOR)
def question_create(request, assignment_pk):
    assignment = get_object_or_404(Assignment, pk=assignment_pk, course__instructors=request.user)
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assignment = assignment
            question.save()
            form.save_choices()
            messages.success(request, "Question created.")
            return redirect("assignment_detail", pk=assignment.pk)
    else:
        form = QuestionForm()
    return render(
        request,
        "core/question_form.html",
        {"form": form, "assignment": assignment},
    )


@role_required(User.Roles.INSTRUCTOR)
def question_edit(request, assignment_pk, question_pk):
    assignment = get_object_or_404(Assignment, pk=assignment_pk, course__instructors=request.user)
    question = get_object_or_404(Question, pk=question_pk, assignment=assignment)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            form.save_choices()
            messages.success(request, "Question updated.")
            return redirect("assignment_detail", pk=assignment.pk)
    else:
        form = QuestionForm(instance=question)
    return render(
        request,
        "core/question_form.html",
        {"form": form, "assignment": assignment, "question": question},
    )


@role_required(User.Roles.INSTRUCTOR)
@require_POST
def question_delete(request, assignment_pk, question_pk):
    assignment = get_object_or_404(Assignment, pk=assignment_pk, course__instructors=request.user)
    question = get_object_or_404(Question, pk=question_pk, assignment=assignment)
    question.delete()
    messages.success(request, "Question deleted.")
    return redirect("assignment_detail", pk=assignment.pk)


@role_required(User.Roles.INSTRUCTOR)
def assignment_submissions(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, course__instructors=request.user)
    submissions = assignment.submissions.select_related("student")
    return render(
        request,
        "core/assignment_submissions.html",
        {"assignment": assignment, "submissions": submissions},
    )


@role_required(User.Roles.INSTRUCTOR)
def grade_submission(request, submission_pk):
    submission = get_object_or_404(Submission, pk=submission_pk, assignment__course__instructors=request.user)
    answers = submission.answers.select_related("question", "selected_choice")
    forms = []
    if request.method == "POST":
        valid = True
        for answer in answers:
            form = SubmissionFeedbackForm(
                request.POST, instance=answer, prefix=str(answer.pk)
            )
            forms.append(form)
            if not form.is_valid():
                valid = False
        if valid:
            total = Decimal("0")
            for form in forms:
                answer = form.save()
                if answer.score is not None:
                    total += answer.score
            submission.total_score = total
            submission.graded_at = timezone.now()
            submission.save(update_fields=["total_score", "graded_at"])
            messages.success(request, "Submission graded.")
            return redirect("assignment_submissions", pk=submission.assignment.pk)
    else:
        for answer in answers:
            forms.append(
                SubmissionFeedbackForm(instance=answer, prefix=str(answer.pk))
            )
    return render(
        request,
        "core/submission_grade.html",
        {"submission": submission, "forms": zip(answers, forms)},
    )


@role_required(User.Roles.INSTRUCTOR)
def publish_submission(request, submission_pk):
    submission = get_object_or_404(Submission, pk=submission_pk, assignment__course__instructors=request.user)
    submission.published = True
    submission.save(update_fields=["published"])
    messages.success(request, "Submission published.")
    return redirect("assignment_submissions", pk=submission.assignment.pk)


@role_required(User.Roles.INSTRUCTOR)
def export_assignment_csv(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, course__instructors=request.user)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename=assignment_{assignment.pk}.csv"
    writer = csv.writer(response)
    writer.writerow(["Student", "Question", "Response", "Score", "Max Points", "Late", "Published"])
    for submission in assignment.submissions.select_related("student"):
        for answer in submission.answers.select_related("question"):
            writer.writerow(
                [
                    submission.student.get_full_name() or submission.student.username,
                    answer.question.prompt,
                    answer.response_text or (answer.selected_choice.text if answer.selected_choice else ""),
                    answer.score,
                    answer.question.points,
                    "Yes" if submission.is_late else "No",
                    "Yes" if submission.published else "No",
                ]
            )
    return response


@role_required(User.Roles.INSTRUCTOR)
def analytics_view(request):
    courses = (
        request.user.courses_instructing.annotate(
            assignment_count=Count("assignments", distinct=True),
            average_score=Avg("assignments__submissions__total_score"),
        )
        .prefetch_related("assignments")
        .all()
    )
    assignments = (
        Assignment.objects.filter(course__instructors=request.user)
        .annotate(
            submission_count=Count("submissions", distinct=True),
            average_score=Avg("submissions__total_score"),
        )
        .select_related("course")
    )
    return render(
        request,
        "core/analytics.html",
        {"courses": courses, "assignments": assignments},
    )


@role_required(User.Roles.STUDENT)
def student_dashboard(request):
    assignments = (
        Assignment.objects.filter(course__students=request.user)
        .select_related("course")
        .order_by("due_date")
    )
    submissions = {s.assignment_id: s for s in Submission.objects.filter(student=request.user)}
    return render(
        request,
        "core/student_dashboard.html",
        {"assignments": assignments, "submissions": submissions},
    )


@role_required(User.Roles.STUDENT)
def assignment_take(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, course__students=request.user)
    existing_submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    form = SubmissionForm(assignment, request.POST or None, submission=existing_submission)
    if request.method == "POST" and form.is_valid():
        submission, created = Submission.objects.get_or_create(
            assignment=assignment, student=request.user
        )
        submission.submitted_at = timezone.now()
        submission.is_late = submission.submitted_at > assignment.due_date
        submission.save()
        for question in assignment.questions.all():
            field_name = f"question_{question.id}"
            value = form.cleaned_data.get(field_name)
            answer, _ = SubmissionAnswer.objects.get_or_create(
                submission=submission, question=question
            )
            if question.question_type == Question.QuestionTypes.MULTIPLE_CHOICE:
                choice = question.choices.get(pk=value)
                answer.selected_choice = choice
                answer.response_text = choice.text
            else:
                answer.response_text = value
                answer.selected_choice = None
            answer.score = None
            answer.save()
        submission.auto_grade()
        messages.success(request, "Assignment submitted.")
        return redirect("student_dashboard")
    return render(
        request,
        "core/assignment_take.html",
        {"assignment": assignment, "form": form},
    )


@role_required(User.Roles.STUDENT)
def submission_detail(request, submission_pk):
    submission = get_object_or_404(Submission, pk=submission_pk, student=request.user)
    answers = submission.answers.select_related("question", "selected_choice")
    return render(
        request,
        "core/submission_detail.html",
        {"submission": submission, "answers": answers},
    )

# Create your views here.
