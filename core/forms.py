from django import forms
from django.utils import timezone

from .models import Assignment, Choice, Course, Question, SubmissionAnswer


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "code", "description", "students"]


class AssignmentForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )

    class Meta:
        model = Assignment
        fields = ["course", "title", "description", "due_date", "published"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.due_date:
            localized = timezone.localtime(self.instance.due_date)
            self.initial["due_date"] = localized.strftime("%Y-%m-%dT%H:%M")


class QuestionForm(forms.ModelForm):
    option_1 = forms.CharField(required=False, label="Option A")
    option_2 = forms.CharField(required=False, label="Option B")
    option_3 = forms.CharField(required=False, label="Option C")
    option_4 = forms.CharField(required=False, label="Option D")
    option_5 = forms.CharField(required=False, label="Option E")
    correct_option = forms.ChoiceField(
        required=False,
        choices=[(label, label) for label in ["A", "B", "C", "D", "E"]],
    )

    class Meta:
        model = Question
        fields = [
            "prompt",
            "question_type",
            "points",
            "order",
            "rubric",
            "correct_answer",
        ]
        widgets = {
            "prompt": forms.Textarea(attrs={"rows": 3}),
            "rubric": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.question_type == Question.QuestionTypes.MULTIPLE_CHOICE:
            for label, option_field in zip(["A", "B", "C", "D", "E"], [
                "option_1",
                "option_2",
                "option_3",
                "option_4",
                "option_5",
            ]):
                choice = self.instance.choices.filter(label=label).first()
                if choice:
                    self.fields[option_field].initial = choice.text
                    if choice.is_correct:
                        self.fields["correct_option"].initial = label

    def save(self, commit=True):
        question = super().save(commit)
        self._question = question
        return question

    def save_choices(self):
        question = getattr(self, "_question", None)
        if not question:
            return
        if question.question_type == Question.QuestionTypes.MULTIPLE_CHOICE:
            labels = ["A", "B", "C", "D", "E"]
            choice_texts = [
                self.cleaned_data.get("option_1"),
                self.cleaned_data.get("option_2"),
                self.cleaned_data.get("option_3"),
                self.cleaned_data.get("option_4"),
                self.cleaned_data.get("option_5"),
            ]
            correct = self.cleaned_data.get("correct_option")
            question.choices.all().delete()
            for label, text in zip(labels, choice_texts):
                if text:
                    Choice.objects.create(
                        question=question,
                        label=label,
                        text=text,
                        is_correct=label == correct,
                    )


class SubmissionFeedbackForm(forms.ModelForm):
    class Meta:
        model = SubmissionAnswer
        fields = ["score", "feedback"]
        widgets = {
            "feedback": forms.Textarea(attrs={"rows": 2}),
        }


class SubmissionForm(forms.Form):
    def __init__(self, assignment, *args, submission=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.assignment = assignment
        for question in assignment.questions.all():
            field_name = f"question_{question.id}"
            if question.question_type == Question.QuestionTypes.MULTIPLE_CHOICE:
                self.fields[field_name] = forms.ChoiceField(
                    label=question.prompt,
                    choices=[(choice.id, choice.text) for choice in question.choices.all()],
                    widget=forms.RadioSelect,
                )
            elif question.question_type == Question.QuestionTypes.SHORT_RESPONSE:
                self.fields[field_name] = forms.CharField(
                    label=question.prompt,
                    widget=forms.TextInput(),
                )
            else:
                self.fields[field_name] = forms.CharField(
                    label=question.prompt,
                    widget=forms.Textarea(attrs={"rows": 4}),
                )
            if submission:
                answer = submission.answers.filter(question=question).first()
                if answer:
                    if question.question_type == Question.QuestionTypes.MULTIPLE_CHOICE and answer.selected_choice:
                        self.fields[field_name].initial = answer.selected_choice.pk
                    else:
                        self.fields[field_name].initial = answer.response_text
