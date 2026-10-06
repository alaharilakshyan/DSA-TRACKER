from django import forms
from .models import Problem, Attempt, Topic


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ["title", "topic", "pattern", "supporting_concepts", "difficulty", "link", "notes", "is_mastered"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g., Two Sum, Trapping Rain Water, LRU Cache",
                "required": "required",
            }),
            "topic": forms.Select(attrs={
                "class": "form-select",
                "required": "required",
            }),
            "pattern": forms.Select(attrs={
                "class": "form-select",
            }),
            "supporting_concepts": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Supporting concepts, e.g. HashMap, Two Pointers, Binary Search",
            }),
            "difficulty": forms.Select(attrs={
                "class": "form-select",
                "required": "required",
            }),
            "link": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://leetcode.com/problems/...",
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Key takeaways, intuition, time/space complexity, edge cases to remember...",
            }),
            "is_mastered": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }


class AttemptForm(forms.ModelForm):
    class Meta:
        model = Attempt
        fields = ["time_taken_minutes", "was_successful", "approach_notes"]
        widgets = {
            "time_taken_minutes": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "max": "600",
                "placeholder": "Minutes taken (e.g. 25)",
                "required": "required",
            }),
            "was_successful": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
            "approach_notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "What approach worked? What mistakes or edge cases did you hit?",
            }),
        }


class RevisionQualityForm(forms.Form):
    QUALITY_CHOICES = [
        ("0", "0 — Total Blackout (no recall)"),
        ("1", "1 — Incorrect (remembered after seeing solution)"),
        ("2", "2 — Incorrect (serious hesitation / flawed logic)"),
        ("3", "3 — Correct with serious difficulty / slow recall"),
        ("4", "4 — Correct after slight hesitation"),
        ("5", "5 — Perfect recall (instant & clear intuition)"),
    ]
    quality = forms.ChoiceField(
        choices=QUALITY_CHOICES,
        label="How well did you recall the solution?",
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        initial="4",
    )
