from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Topic"
        verbose_name_plural = "Topics"

    def __str__(self):
        return self.name


class Problem(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "EASY", "Easy"
        MEDIUM = "MEDIUM", "Medium"
        HARD = "HARD", "Hard"

    class Pattern(models.TextChoices):
        TWO_POINTER = "TWO_POINTER", "Two Pointers"
        FAST_SLOW = "FAST_SLOW", "Fast & Slow Pointers"
        SLIDING_WINDOW = "SLIDING_WINDOW", "Sliding Window"
        INTERVALS = "INTERVALS", "Merge Intervals"
        MONOTONIC_STACK = "MONOTONIC_STACK", "Monotonic Stack / Queue"
        DP = "DP", "Dynamic Programming"
        BACKTRACKING = "BACKTRACKING", "Backtracking"
        GREEDY = "GREEDY", "Greedy"
        GRAPH = "GRAPH", "Graph Traversal (BFS/DFS)"
        UNION_FIND = "UNION_FIND", "Union Find / Disjoint Set"
        BINARY_SEARCH = "BINARY_SEARCH", "Binary Search"
        HEAP_TOP_K = "HEAP_TOP_K", "Top 'K' Elements (Heap)"
        TREE_TRAVERSAL = "TREE_TRAVERSAL", "Tree BFS / DFS"
        TRIE = "TRIE", "Trie / Prefix Tree"
        BIT_MANIPULATION = "BIT_MANIPULATION", "Bit Manipulation"
        OTHER = "OTHER", "Other / General"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="problems")
    title = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="problems")
    pattern = models.CharField(max_length=30, choices=Pattern.choices, default=Pattern.OTHER)
    supporting_concepts = models.CharField(
        max_length=255,
        blank=True,
        help_text="Supporting DSA concepts, e.g. HashMap, Two Pointers, Prefix Sum"
    )
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices)
    link = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    is_mastered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Problem"
        verbose_name_plural = "Problems"

    def __str__(self):
        return self.title

    @property
    def latest_attempt(self):
        return self.attempts.first()

    @property
    def attempts_count(self):
        return self.attempts.count()

    @property
    def difficulty_badge_class(self):
        return {
            "EASY": "badge-difficulty-easy",
            "MEDIUM": "badge-difficulty-medium",
            "HARD": "badge-difficulty-hard",
        }.get(self.difficulty, "badge-difficulty-medium")

    @property
    def supporting_concepts_list(self):
        if not self.supporting_concepts:
            return []
        return [c.strip() for c in self.supporting_concepts.split(",") if c.strip()]


class Attempt(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="attempts")
    solved_at = models.DateTimeField(default=timezone.now)
    time_taken_minutes = models.PositiveIntegerField(help_text="Time taken in minutes")
    was_successful = models.BooleanField(default=True)
    approach_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-solved_at"]
        verbose_name = "Attempt"
        verbose_name_plural = "Attempts"

    def __str__(self):
        status = "Success" if self.was_successful else "Failed"
        return f"{self.problem.title} ({status}) - {self.time_taken_minutes} mins"


class RevisionSchedule(models.Model):
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, related_name="revision")
    ease_factor = models.FloatField(default=2.5)
    interval_days = models.PositiveIntegerField(default=1)
    repetitions = models.PositiveIntegerField(default=0)
    next_review_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Revision for {self.problem.title} on {self.next_review_date}"

    @property
    def is_due_today(self):
        return self.next_review_date <= timezone.now().date()


# ---------------------------------------------------------
# CANONICAL QUESTION BANK & INTERVIEW SIMULATOR MODELS
# ---------------------------------------------------------

class CanonicalInterviewQuestion(models.Model):
    class Track(models.TextChoices):
        GENERAL = "GENERAL", "General SDE"
        FRONTEND = "FRONTEND", "Frontend Engineering"
        BACKEND = "BACKEND", "Backend & Distributed Systems"
        PRODUCT = "PRODUCT", "Product-Based (FAANG/MAMAA)"

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.SET_NULL, related_name="canonical_questions")
    pattern = models.CharField(max_length=30, choices=Problem.Pattern.choices, default=Problem.Pattern.OTHER)
    supporting_concepts = models.CharField(max_length=255, blank=True)
    difficulty = models.CharField(max_length=10, choices=Problem.Difficulty.choices)
    target_tracks = models.CharField(
        max_length=200,
        default="GENERAL,BACKEND,PRODUCT",
        help_text="Comma-separated tracks: GENERAL, FRONTEND, BACKEND, PRODUCT"
    )
    company_tags = models.CharField(max_length=200, blank=True, help_text="e.g. Google, Meta, Amazon")
    description = models.TextField()
    examples = models.TextField(blank=True)
    constraints = models.TextField(blank=True)
    hints = models.JSONField(default=list, help_text="List of tiered hints (1: Intuition, 2: DS, 3: Approach)")
    follow_ups = models.JSONField(default=list, help_text="List of interviewer follow-ups with answers")
    optimal_time_complexity = models.CharField(max_length=50, blank=True)
    optimal_space_complexity = models.CharField(max_length=50, blank=True)
    leetcode_url = models.URLField(blank=True)

    class Meta:
        ordering = ["difficulty", "title"]
        verbose_name = "Canonical Interview Question"
        verbose_name_plural = "Canonical Interview Questions"

    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()} - {self.get_pattern_display()})"


class InterviewSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interview_sessions")
    track = models.CharField(max_length=50, default="GENERAL")
    difficulty = models.CharField(max_length=20, default="MEDIUM")
    duration_minutes = models.PositiveIntegerField(default=45)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    score = models.FloatField(default=0.0)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Interview Session"
        verbose_name_plural = "Interview Sessions"

    def __str__(self):
        return f"{self.user.username} - {self.track} ({self.difficulty}) on {self.started_at.strftime('%Y-%m-%d')}"

    @property
    def questions_count(self):
        return self.questions.count()


class InterviewQuestionAttempt(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="questions")
    canonical_question = models.ForeignKey(CanonicalInterviewQuestion, null=True, blank=True, on_delete=models.SET_NULL)
    user_problem = models.ForeignKey(Problem, null=True, blank=True, on_delete=models.SET_NULL)
    question_order = models.PositiveIntegerField(default=1)
    time_taken_seconds = models.PositiveIntegerField(default=0)
    hints_revealed = models.PositiveIntegerField(default=0)
    candidate_code = models.TextField(blank=True)
    candidate_approach = models.TextField(blank=True)
    follow_up_answer = models.TextField(blank=True)
    was_passed = models.BooleanField(default=False)
    feedback_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["question_order"]

    def __str__(self):
        q_title = self.canonical_question.title if self.canonical_question else (self.user_problem.title if self.user_problem else f"Question {self.question_order}")
        return f"Q{self.question_order}: {q_title} in Session #{self.session.id}"


class InterviewReport(models.Model):
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name="report")
    overall_score = models.FloatField(default=0.0)
    problem_solving_score = models.FloatField(default=0.0)
    pattern_recognition_score = models.FloatField(default=0.0)
    time_management_score = models.FloatField(default=0.0)
    optimization_score = models.FloatField(default=0.0)
    consistency_score = models.FloatField(default=0.0)
    weak_area = models.CharField(max_length=150, blank=True)
    recommended_patterns = models.JSONField(default=list)
    revision_roadmap = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for Session #{self.session.id} - {self.overall_score}%"
