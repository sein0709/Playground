from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("instructor/", views.instructor_dashboard, name="instructor_dashboard"),
    path("instructor/courses/", views.course_list, name="course_list"),
    path("instructor/courses/new/", views.course_create, name="course_create"),
    path("instructor/courses/<int:pk>/", views.course_detail, name="course_detail"),
    path("instructor/assignments/new/", views.assignment_create, name="assignment_create"),
    path("instructor/assignments/<int:pk>/", views.assignment_detail, name="assignment_detail"),
    path("instructor/assignments/<int:pk>/edit/", views.assignment_edit, name="assignment_edit"),
    path(
        "instructor/assignments/<int:assignment_pk>/questions/new/",
        views.question_create,
        name="question_create",
    ),
    path(
        "instructor/assignments/<int:assignment_pk>/questions/<int:question_pk>/edit/",
        views.question_edit,
        name="question_edit",
    ),
    path(
        "instructor/assignments/<int:assignment_pk>/questions/<int:question_pk>/delete/",
        views.question_delete,
        name="question_delete",
    ),
    path(
        "instructor/assignments/<int:pk>/submissions/",
        views.assignment_submissions,
        name="assignment_submissions",
    ),
    path("instructor/submissions/<int:submission_pk>/grade/", views.grade_submission, name="grade_submission"),
    path(
        "instructor/submissions/<int:submission_pk>/publish/",
        views.publish_submission,
        name="publish_submission",
    ),
    path(
        "instructor/assignments/<int:pk>/export/",
        views.export_assignment_csv,
        name="export_assignment_csv",
    ),
    path("instructor/analytics/", views.analytics_view, name="analytics"),
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("student/assignments/<int:pk>/", views.assignment_take, name="assignment_take"),
    path(
        "student/submissions/<int:submission_pk>/",
        views.submission_detail,
        name="submission_detail",
    ),
]
