from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Roles(models.TextChoices):
        INSTRUCTOR = "instructor", "Instructor"
        STUDENT = "student", "Student"

    role = models.CharField(max_length=20, choices=Roles.choices)

    def is_instructor(self):
        return self.role == self.Roles.INSTRUCTOR

    def is_student(self):
        return self.role == self.Roles.STUDENT


class Course(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    instructors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="courses_instructing",
        limit_choices_to={"role": User.Roles.INSTRUCTOR},
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="courses_enrolled",
        blank=True,
        limit_choices_to={"role": User.Roles.STUDENT},
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class Assignment(models.Model):
    course = models.ForeignKey(Course, related_name="assignments", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="assignments_created", on_delete=models.CASCADE
    )
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_points(self):
        return sum((question.points for question in self.questions.all()), Decimal("0"))

    def __str__(self):
        return f"{self.course.code}: {self.title}"


class Question(models.Model):
    class QuestionTypes(models.TextChoices):
        FREE_RESPONSE = "free", "Free Response"
        SHORT_RESPONSE = "short", "Short Response"
        MULTIPLE_CHOICE = "mcq", "Multiple Choice"

    assignment = models.ForeignKey(
        Assignment, related_name="questions", on_delete=models.CASCADE
    )
    prompt = models.TextField()
    question_type = models.CharField(max_length=10, choices=QuestionTypes.choices)
    points = models.DecimalField(max_digits=6, decimal_places=2)
    order = models.PositiveIntegerField(default=0)
    rubric = models.TextField(blank=True)
    correct_answer = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.assignment.title} - {self.prompt[:25]}"


class Choice(models.Model):
    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE
    )
    label = models.CharField(max_length=1)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ("question", "label")
        ordering = ["label"]

    def __str__(self):
        return f"{self.label}. {self.text}"


class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment, related_name="submissions", on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="submissions", on_delete=models.CASCADE
    )
    submitted_at = models.DateTimeField(default=timezone.now)
    is_late = models.BooleanField(default=False)
    total_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    published = models.BooleanField(default=False)

    class Meta:
        unique_together = ("assignment", "student")
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.assignment} - {self.student.username}"

    def auto_grade(self):
        total = Decimal("0")
        graded = False
        for answer in self.answers.select_related("question", "selected_choice"):
            question = answer.question
            score = None
            if question.question_type == Question.QuestionTypes.MULTIPLE_CHOICE:
                if answer.selected_choice and answer.selected_choice.is_correct:
                    score = question.points
                else:
                    score = 0
            elif question.question_type == Question.QuestionTypes.SHORT_RESPONSE:
                expected = (question.correct_answer or "").strip().lower()
                response = (answer.response_text or "").strip().lower()
                score = question.points if expected and response == expected else 0
            if score is not None:
                answer.score = score
                answer.save(update_fields=["score"])
                total += Decimal(score)
                graded = True
        if graded:
            self.total_score = total
            self.graded_at = timezone.now()
            self.save(update_fields=["total_score", "graded_at"])


class SubmissionAnswer(models.Model):
    submission = models.ForeignKey(
        Submission, related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response_text = models.TextField(blank=True)
    selected_choice = models.ForeignKey(
        Choice, null=True, blank=True, on_delete=models.SET_NULL
    )
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ("submission", "question")

    def __str__(self):
        return f"Answer to {self.question}"

# Create your models here.
