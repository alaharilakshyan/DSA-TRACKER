from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from tracker.models import Problem, RevisionSchedule, Attempt


def get_topic_progress(user):
    """Returns total and mastered problems per topic for the user."""
    return (
        user.problems.values("topic__id", "topic__name", "topic__slug")
        .annotate(
            total=Count("id"),
            mastered=Count("id", filter=Q(is_mastered=True)),
        )
        .order_by("topic__name")
    )


def get_weak_patterns(user, limit=5):
    """Patterns with the highest average time-to-solve — a proxy for 'weak area'."""
    return (
        user.problems.values("pattern")
        .annotate(
            avg_time=Avg("attempts__time_taken_minutes"),
            problem_count=Count("id", distinct=True),
            attempt_count=Count("attempts__id", distinct=True)
        )
        .exclude(avg_time__isnull=True)
        .order_by("-avg_time")[:limit]
    )


def get_difficulty_breakdown(user):
    """Returns problem counts per difficulty level (Easy, Medium, Hard)."""
    return (
        user.problems.values("difficulty")
        .annotate(
            total=Count("id"),
            mastered=Count("id", filter=Q(is_mastered=True)),
        )
    )


def get_dashboard_kpis(user):
    """Aggregates high-level metrics for the user dashboard."""
    total_problems = user.problems.count()
    mastered_problems = user.problems.filter(is_mastered=True).count()
    mastery_rate = round((mastered_problems / total_problems * 100), 1) if total_problems > 0 else 0

    attempts = Attempt.objects.filter(problem__user=user)
    total_attempts = attempts.count()
    successful_attempts = attempts.filter(was_successful=True).count()
    success_rate = round((successful_attempts / total_attempts * 100), 1) if total_attempts > 0 else 0
    total_time_mins = attempts.aggregate(total_time=Sum("time_taken_minutes"))["total_time"] or 0

    today = timezone.now().date()
    revisions_due = RevisionSchedule.objects.filter(
        problem__user=user,
        next_review_date__lte=today,
    ).count()

    return {
        "total_problems": total_problems,
        "mastered_problems": mastered_problems,
        "mastery_rate": mastery_rate,
        "total_attempts": total_attempts,
        "success_rate": success_rate,
        "total_time_minutes": total_time_mins,
        "revisions_due_today": revisions_due,
    }
