# Playground
## Assignments Portal

This repository now contains a Django-based web application for managing school assignments with role-based dashboards for instructors and students.

### Features

- Custom user model with Instructor and Student roles.
- Course management for instructors, including roster assignment.
- Assignment creation with title, description, course, due date, publishing, and per-question point totals.
- Question authoring supporting free-response (with rubrics), short-response (auto-graded), and multiple-choice (five-option) types.
- Student assignment submission with late flagging and automatic scoring for multiple-choice and short-response questions.
- Manual grading workflow for free-response answers, including per-question feedback and rubric display.
- Grade publishing controls and CSV export of submissions.
- Analytics dashboards summarizing performance by course and assignment.

### Getting Started

1. Install dependencies and run migrations:

   ```bash
   pip install -r requirements.txt  # or pip install django==4.2.7
   python manage.py migrate
   ```

2. Create a superuser and assign roles to users through the Django admin:

   ```bash
   python manage.py createsuperuser
   ```

3. Start the development server:

   ```bash
   python manage.py runserver
   ```

4. Visit `http://localhost:8000/` to sign in and access the appropriate dashboard based on your role.
